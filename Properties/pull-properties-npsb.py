import requests
import logging
import json
from dotenv import load_dotenv
import os

# Loads the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('NPSB_API_KEY')  # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API

# Set the headers, including the API key
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Initialize an empty list to store property data
retrieved_properties = []

# HubSpot API endpoint for retrieving all contact properties
url = f'{BASE_API_URL}/crm/v3/properties/contacts'

# Make the GET request to retrieve all contact properties
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    properties_data = response.json().get('results', [])
    
    # Loop through each property and append relevant details
    for property_data in properties_data:
        # Collect the options if the property has any
        options = property_data.get('options', [])
        formatted_options = [
            {
                'label': option.get('label'),
                'value': option.get('value'),
                'description': option.get('description'),
                'displayOrder': option.get('displayOrder'),
                'hidden': option.get('hidden')
            }
            for option in options
        ]

        # Append the property details, including options
        retrieved_properties.append({
            'name': property_data.get('name'),
            'label': property_data.get('label'),
            'type': property_data.get('type'),
            'fieldType': property_data.get('fieldType'),
            'description': property_data.get('description'),
            'groupName': property_data.get('groupName'),
            'options': formatted_options if formatted_options else None  # Include options if available
        })
    
    # Write the retrieved properties to a JSON file
    with open('contact_properties_with_options.json', mode='w') as json_file:
        json.dump(retrieved_properties, json_file, indent=4)
    
    print("Contact properties with options have been saved to contact_properties_with_options.json")
else:
    print(f"Failed to retrieve contact properties. Status code: {response.status_code}")
    print(f"Error details: {response.text}")