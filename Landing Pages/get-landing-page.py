import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
ACCESS_TOKEN = os.getenv('MIP_API_KEY')  # Replace with your HubSpot account Access Token
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
OUTPUT_FILE = 'landing_page_details.json'  # File to save the exported landing page details

# Configure logging
logging.basicConfig(
    filename='landing_page_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log the Access Token (CAUTION: Only do this in a secure environment)
logging.debug(f"Access Token used: {ACCESS_TOKEN}")

# Function to export landing page details from HubSpot
def export_landing_page(page_id):
    url = f'{BASE_API_URL}/cms/v3/pages/landing-pages/{page_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'  # Pass the Access Token in the Authorization header
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        logging.info(f"Successfully retrieved landing page details for ID {page_id}")
        return response.json()  # Return the response as a JSON object
    else:
        logging.error(f"Failed to retrieve landing page details for ID {page_id}: {response.status_code} - {response.text}")
        return None

def main():
    # Prompt user for the landing page ID
    page_id = input("Enter the Landing Page ID: ")
    
    # Export the landing page details
    page_data = export_landing_page(page_id)
    
    if page_data:
        # Save the landing page details to a JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(page_data, f, indent=4)
        
        logging.info(f"Landing page details saved to {OUTPUT_FILE}")
        print(f"Landing page details saved to {OUTPUT_FILE}")
    else:
        print(f"Failed to retrieve or save landing page details for ID {page_id}")

if __name__ == "__main__":
    main()
