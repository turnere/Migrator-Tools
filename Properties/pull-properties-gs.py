import requests
import logging
import csv
from dotenv import load_dotenv
import os

# Loads the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('GS_API_KEY')   # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API

# Set the headers, including the API key
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# List to store property names from the CSV
property_names = []

# Read property names from a CSV file
with open('property_names.csv', mode='r', newline='', encoding='ISO-8859-1') as csv_file:
    csv_reader = csv.reader(csv_file)
    
    # Skip the header if there is one
    next(csv_reader, None)
    
    # Loop through each row and get the property name
    for row in csv_reader:
        if row:  # Ensure the row is not empty
            property_names.append(row[0])  # Assuming the property name is in the first column

# Initialize an empty list to store property data
retrieved_properties = []

# Loop through each property name and fetch its details
for property_name in property_names:
    # HubSpot API endpoint for retrieving specific contact property by name
    url = f'{BASE_API_URL}/crm/v3/properties/contacts/{property_name}'
    
    # Make the GET request to retrieve the specific contact property
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        property_data = response.json()

        # Append the retrieved property data to the list
        retrieved_properties.append({
            'name': property_data.get('name'),
            'label': property_data.get('label'),
            'type': property_data.get('type'),
            'fieldType': property_data.get('fieldType'),  # Include 'fieldType'
            'groupName': property_data.get('groupName')
        })
    else:
        print(f"Failed to retrieve property '{property_name}'. Status code: {response.status_code}")
        print(f"Error details: {response.text}")

# Write the retrieved properties to a CSV file
with open('specific_contact_properties.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header
    writer.writerow(['Property Name', 'Label', 'Type', 'Field Type', 'Group Name'])

    # Write each property to the CSV file
    for property in retrieved_properties:
        writer.writerow([
            property['name'],
            property['label'],
            property['type'],
            property['fieldType'],
            property['groupName']
        ])

print("Specific contact properties have been saved to specific_contact_properties.csv")
