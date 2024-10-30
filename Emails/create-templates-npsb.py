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
JSON_FILE = 'template_details.json'  # The file that contains exported template details

# Configure logging
logging.basicConfig(
    filename='template_import.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to clean up template data before importing to new instance
def clean_template_data(template_data):
    # Remove fields that shouldn't be present when creating a new template
    fields_to_remove = [
        'id', 'createdAt', 'updatedAt', 'archivedAt', 'publishedAt', 'status',
        'appId', 'processingStatus'  # Remove processingStatus as it's read-only
    ]
    
    for field in fields_to_remove:
        template_data.pop(field, None)
    
    return template_data

# Function to create a new template in the new HubSpot instance
def create_template(template_data):
    url = f'{BASE_API_URL}/content/api/v2/templates'
    headers = {
        'Authorization': f'Bearer {API_KEY_NEW_INSTANCE}',
        'Content-Type': 'application/json'
    }
    
    # Clean template data
    template_data = clean_template_data(template_data)
    
    # Send POST request to create the template
    response = requests.post(url, headers=headers, json=template_data)
    
    # Check for errors
    if response.status_code == 201:
        logging.info(f"Successfully created template: {json.dumps(response.json(), indent=4)}")
        return response.json()
    else:
        logging.error(f"Failed to create template: {response.status_code} - {response.text}")
        return None

def main():
    # Load template data from JSON file
    with open(JSON_FILE, 'r') as f:
        templates = json.load(f)
    
    # Iterate over each template in the JSON file and create it
    for template_data in templates:
        create_template(template_data)

if __name__ == "__main__":
    main()
