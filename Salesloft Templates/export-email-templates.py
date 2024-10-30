import requests
import logging
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLMIP_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2'

# Configure logging
logging.basicConfig(
    filename='email_templates_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch an email template by ID
def fetch_email_template_by_id(template_id):
    url = f'{BASE_API_URL}/email_templates/{template_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching email template with ID {template_id} from {url}")  # Log the request

    response = requests.get(url, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        logging.error(f"Error fetching email template {template_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()  # Parse the response JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Email template {template_id} fetched successfully")
    return data

# Function to save all email template data into a single JSON file
def save_all_email_templates(templates_data):
    filename = 'all_email_templates.json'
    with open(filename, 'w') as json_file:
        json.dump(templates_data, json_file, indent=4)
    logging.info(f"All email templates data saved to {filename}")

def main():
    template_ids = ['122305490']  # List of email template IDs to fetch
    all_email_templates = []  # List to store all fetched templates

    for template_id in template_ids:
        logging.info(f"Processing email template ID: {template_id}")  # Log the current template ID
        email_template_data = fetch_email_template_by_id(template_id)

        if email_template_data:
            all_email_templates.append(email_template_data)  # Add the fetched template data to the list
        else:
            logging.info(f"No data found for email template ID: {template_id}")

    # If any templates were fetched, save them to a single JSON file
    if all_email_templates:
        save_all_email_templates(all_email_templates)
    else:
        logging.info("No email template data to save.")

if __name__ == "__main__":
    main()
