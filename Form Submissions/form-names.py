import requests
import pandas as pd
import logging
from dotenv import load_dotenv
import os

# Constants
load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv('MIP_API_KEY')  # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com/marketing/v3/forms/'  # Base URL for HubSpot Forms API

# Configure logging
logging.basicConfig(
    filename='fetch_form_names.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_form_details(form_id):
    """
    Fetch the form details, including name, form ID, and updatedAt.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    form_url = f"{BASE_API_URL}{form_id}"
    logging.debug(f"Fetching form details for form ID: {form_id}")
    
    response = requests.get(form_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        form_name = data.get('name')
        updated_at = data.get('updatedAt')
        return form_id, form_name, updated_at
    else:
        logging.error(f"Failed to fetch form details for {form_id}: {response.status_code} - {response.text}")
        return form_id, None, None

def main():
    # Load form IDs from CSV file
    df_form_ids = pd.read_csv('mip_form_ids.csv')  # Assuming CSV has a column "Form ID"
    form_ids = df_form_ids['Form ID'].tolist()  # Extract form IDs from CSV
    
    all_results = []  # List to store results (form_id, form_name, updated_at)
    
    for form_id in form_ids:
        logging.info(f"Processing form ID: {form_id}")
        form_id, form_name, updated_at = fetch_form_details(form_id)
        
        if form_name:
            all_results.append((form_id, form_name, updated_at))  # Add form ID, form name, and updatedAt to results
        else:
            logging.info(f"No form name found for form ID: {form_id}")
    
    # Convert the list to a DataFrame with 'Form ID', 'Form Name', and 'Updated At' columns
    df = pd.DataFrame(all_results, columns=['Form ID', 'Form Name', 'Updated At'])
    
    # Save to CSV
    df.to_csv('gs_form_ids_names_and_updated_at.csv', index=False)
    logging.info("Data saved to gs_form_ids_names_and_updated_at.csv")

if __name__ == "__main__":
    main()
