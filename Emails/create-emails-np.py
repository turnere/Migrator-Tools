import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
API_KEY_NEW_INSTANCE = os.getenv('NP_API_KEY')  # Replace with your new HubSpot account API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
JSON_FILE = 'email_details.json'  # The file that contains exported email details

# Configure logging
logging.basicConfig(
    filename='email_import.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to clean up email data before importing to new instance
def clean_email_data(email_data):
    # Remove fields that shouldn't be present when creating a new email
    fields_to_remove = [
        'id', 'createdAt', 'updatedAt', 'archivedAt', 'publishedAt', 'status', 
        'appId', 'processingStatus', 'subscription', 'subscriptionName',  # Remove subscription and subscriptionName
        'businessUnitId'  # Remove businessUnitId as well
    ]
    
    for field in fields_to_remove:
        email_data.pop(field, None)
    
    # Set the state to DRAFT to avoid issues with the email being published
    email_data['state'] = 'DRAFT'
    
    return email_data

# Function to create a new email in the new HubSpot instance using legacy API endpoint
def create_email(email_data):
    # Using the legacy API endpoint
    url = f'{BASE_API_URL}/marketing-emails/v1/emails/'
    headers = {
        'Authorization': f'Bearer {API_KEY_NEW_INSTANCE}',
        'Content-Type': 'application/json'
    }
    
    # Clean email data
    email_data = clean_email_data(email_data)
    
    # Log cleaned data before making the request
    logging.debug(f"Creating email with the following data: {json.dumps(email_data, indent=4)}")
    
    # Send POST request to create the email
    response = requests.post(url, headers=headers, json=email_data)
    
    # Check for errors
    if response.status_code == 201:
        logging.info(f"Successfully created email: {json.dumps(response.json(), indent=4)}")
        return response.json()
    else:
        # Log detailed error message
        logging.error(f"Failed to create email: {response.status_code} - {response.text}")
        print(f"Error: {response.status_code} - {response.json().get('message')}")
        return None

def main():
    # Load email data from JSON file
    with open(JSON_FILE, 'r') as f:
        emails = json.load(f)
    
    # Iterate over each email in the JSON file and create it in the new instance
    for email_data in emails:
        create_email(email_data)

if __name__ == "__main__":
    main()