import requests
import json
import logging
from dotenv import load_dotenv
import os
import csv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('GS_API_KEY')  # Replace with your HubSpot account API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
CSV_FILE = 'template_ids.csv'  # CSV file containing template IDs
OUTPUT_FILE = 'template_details.json'  # File to save the exported template details

# Configure logging
logging.basicConfig(
    filename='template_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log the API key (CAUTION: Only do this in a secure environment)
logging.debug(f"API Key used: {API_KEY}")

# Function to export template details from HubSpot
def export_template(template_id):
    url = f'{BASE_API_URL}/content/api/v2/templates/{template_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'  # Pass API key in Authorization header
    }

    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        logging.info(f"Successfully retrieved template details for ID {template_id}")
        template_data = response.json()
        return template_data
    else:
        logging.error(f"Failed to retrieve template details for ID {template_id}: {response.status_code} - {response.text}")
        return None

def main():
    templates = []  # List to store all template details

    # Read template IDs from CSV file
    with open(CSV_FILE, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            template_id = row[0]  # Assuming each row has only one column with the template ID
            logging.info(f"Processing template ID: {template_id}")
            
            # Export the template details
            template_data = export_template(template_id)
            
            if template_data:
                templates.append(template_data)  # Add the template data to the list

    # Save all template details to a JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(templates, f, indent=4)
    
    logging.info(f"All template details saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
