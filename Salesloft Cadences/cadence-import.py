import requests
import logging
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLGS_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2'

# Configure logging
logging.basicConfig(
    filename='cadence_import.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to create a cadence in SalesLoft using JSON payload
def create_cadence(cadence_data):
    url = f'{BASE_API_URL}/cadence_imports'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Uploading cadence data for import: {cadence_data['settings']['name']}")  # Log the request

    response = requests.post(url, headers=headers, json=cadence_data)

    # Check for HTTP errors
    if response.status_code != 201:
        logging.error(f"Error creating cadence: {response.status_code} - {response.text}")
        return None

    logging.debug(f"Cadence created successfully: {response.json()}")
    return response.json()

def main():
    # Load the transformed cadence data from the JSON file
    file_path = 'transformed_cadence_exports.json'
    
    with open(file_path, 'r') as json_file:
        transformed_data = json.load(json_file)

    # Iterate through each cadence and send it to the API
    for cadence_data in transformed_data:
        created_cadence = create_cadence(cadence_data)

        if created_cadence:
            logging.info(f"Cadence '{cadence_data['settings']['name']}' created successfully.")
        else:
            logging.info(f"Failed to create cadence '{cadence_data['settings']['name']}'.")

if __name__ == "__main__":
    main()
