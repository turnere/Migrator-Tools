import requests
import csv
import json
import os
from dotenv import load_dotenv

# Load the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('NPSB_API_KEY')  # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
OBJECT_TYPE = 'contacts'  # Specify the object type (e.g., 'contacts', 'companies', etc.)

# Set the headers, including the API key
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Read property names from the CSV file
property_names = []
with open('property_names.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        property_names.append(row['Property Name'])  # Ensure the column name is 'Property Name'

# Loop through each property name and retrieve its details
retrieved_properties = []
for property_name in property_names:
    url = f'{BASE_API_URL}/crm/v3/properties/{OBJECT_TYPE}/{property_name}'
    
    # Make the GET request to retrieve the specific property
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response and store the property details
        property_data = response.json()
        retrieved_properties.append(property_data)
        print(f"Successfully retrieved property '{property_name}'")
    else:
        print(f"Failed to retrieve property '{property_name}'. Status code: {response.status_code}")
        print(f"Error details: {response.text}")

# Save the retrieved properties to a JSON file for review
with open('specific_contact_properties.json', mode='w') as json_file:
    json.dump(retrieved_properties, json_file, indent=4)

print("Selected contact properties have been saved to specific_contact_properties.json")

