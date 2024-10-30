import requests
import os
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='property_creation.log', filemode='w')

# Load the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('NP_API_KEY')  # Replace with your actual API key for the new instance
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
OBJECT_TYPE = 'contacts'  # Specify the object type (e.g., 'contacts', 'companies', etc.)

# HubSpot API endpoint for creating a property
url = f'{BASE_API_URL}/crm/v3/properties/{OBJECT_TYPE}'

# Set the headers, including the API key
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Log start of process
logging.info("Starting property creation process...")

# Read the JSON file containing the properties to be created
try:
    with open('contact_properties_with_options.json', mode='r') as file:
        properties_data = json.load(file)

    # Iterate through each property in the JSON data
    for property_data in properties_data:
        property_name = property_data['name']
        label = property_data['label']
        prop_type = property_data['type']
        field_type = property_data['fieldType']  # Get the field type
        group_name = property_data['groupName']
        options = property_data.get('options', [])

        # Log the processing of each property
        logging.info(f"Processing Property: {property_name}")
        if options:
            logging.info(f"Options: {options}")  # Log the options for debugging

        # Construct the property data for the API
        property_payload = {
            'name': property_name,
            'label': label,
            'type': prop_type,
            'fieldType': field_type,  # Include fieldType in the payload
            'groupName': group_name,
        }

        # Include options in the payload if they exist
        if options:
            property_payload['options'] = options

        # Make the POST request to create the property
        response = requests.post(url, headers=headers, json=property_payload)

        # Check if the request was successful
        if response.status_code == 201:
            logging.info(f"Property '{property_name}' created successfully.")
        else:
            logging.error(f"Failed to create property '{property_name}'. Status code: {response.status_code}")
            logging.error(f"Error details: {response.text}")

except FileNotFoundError as e:
    logging.error(f"JSON file not found: {e}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
