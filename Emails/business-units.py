import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
API_KEY_NEW_INSTANCE = os.getenv('NP_API_KEY')  # Replace with your HubSpot API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
JSON_FILE = 'business_units.json'  # The file to save business units

# Configure logging
logging.basicConfig(
    filename='business_units.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch business units from HubSpot
def fetch_business_units():
    url = f'{BASE_API_URL}/marketing/v3/business-units'  # Alternative endpoint for business units
    headers = {
        'Authorization': f'Bearer {API_KEY_NEW_INSTANCE}',
        'Content-Type': 'application/json'
    }

    # Send GET request to fetch business units
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        business_units = response.json()
        logging.info(f"Successfully fetched business units: {json.dumps(business_units, indent=4)}")
        
        # Save business units to JSON file
        with open(JSON_FILE, 'w') as f:
            json.dump(business_units, f, indent=4)
        
        return business_units
    else:
        logging.error(f"Failed to fetch business units: {response.status_code} - {response.text}")
        return None

def main():
    # Fetch and print business units
    business_units = fetch_business_units()
    
    if business_units:
        print("Business units fetched successfully!")
        print(json.dumps(business_units, indent=4))
    else:
        print("Failed to fetch business units.")

if __name__ == "__main__":
    main()
