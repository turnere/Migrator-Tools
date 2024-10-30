import requests
import logging
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLGS_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2/email_templates'
JSON_FILE = 'all_email_templates.json'  # The file where all email templates are stored

# Configure logging
logging.basicConfig(
    filename='email_templates_create.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to create an email template via POST request
def create_email_template(template_data):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    # Access the title within the 'data' object and set it as the name if not present
    if 'title' in template_data['data']:
        if 'name' not in template_data['data']:
            template_data['data']['name'] = template_data['data']['title']
    else:
        logging.error("Template is missing a 'title' field in 'data'. Cannot create this template.")
        return None

    # Log the title to ensure it's present
    logging.debug(f"Creating email template with title: {template_data['data'].get('title', 'No title')}")

    # For debugging, print the template data structure
    logging.debug(f"Template data: {json.dumps(template_data, indent=2)}")

    response = requests.post(BASE_API_URL, headers=headers, json=template_data['data'])

    # Check for HTTP errors
    if response.status_code != 201:
        logging.error(f"Error creating email template: {response.status_code} - {response.text}")
        return None

    logging.debug(f"Email template created successfully: {response.json()}")
    return response.json()

# Function to read email templates from JSON file
def read_email_templates_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            templates = json.load(file)
            logging.info(f"Loaded {len(templates)} email templates from {file_path}")
            return templates
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from file: {file_path}")
        return []

def main():
    # Load email templates from the JSON file
    email_templates = read_email_templates_from_file(JSON_FILE)

    if not email_templates:
        logging.info("No email templates to create.")
        return

    # Iterate over each template and create it in SalesLoft
    for template in email_templates:
        result = create_email_template(template)
        if result:
            logging.info(f"Email template created: {result['id']}")
        else:
            logging.info("Failed to create the email template.")

if __name__ == "__main__":
    main()
