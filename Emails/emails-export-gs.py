import requests
import json
import logging
from dotenv import load_dotenv
import os
import csv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('MIP_API_KEY')  # Replace with your HubSpot account API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
CSV_FILE = 'email_ids.csv'  # CSV file containing email IDs
OUTPUT_FILE = 'email_details.json'  # File to save the exported email details

# Configure logging
logging.basicConfig(
    filename='email_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log the API key (CAUTION: Only do this in a secure environment)
logging.debug(f"API Key used: {API_KEY}")

# Function to export email details from HubSpot
def export_email(email_id):
    url = f'{BASE_API_URL}/marketing-emails/v1/emails/{email_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'  # Pass API key in Authorization header
    }

    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        logging.info(f"Successfully retrieved email details for ID {email_id}")
        return response.json()
    else:
        logging.error(f"Failed to retrieve email details for ID {email_id}: {response.status_code} - {response.text}")
        return None

def main():
    emails = []  # List to store all email details

    # Read email IDs from CSV file
    with open(CSV_FILE, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            email_id = row[0]  # Assuming each row has only one column with the email ID
            logging.info(f"Processing email ID: {email_id}")
            
            # Export the email details
            email_data = export_email(email_id)
            
            if email_data:
                emails.append(email_data)  # Add the email data to the list

    # Save all email details to a JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(emails, f, indent=4)
    
    logging.info(f"All email details saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
