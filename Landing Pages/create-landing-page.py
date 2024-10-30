import requests
import json
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
ACCESS_TOKEN = os.getenv('HS_ACCESS_TOKEN')  # Replace with your HubSpot access token
BASE_API_URL = 'https://api.hubapi.com'
CREATE_LANDING_PAGE_URL = f'{BASE_API_URL}/cms/v3/pages/landing-pages'
EXPORTED_JSON_FILE = 'exported_page_details.json'  # JSON file with the exported page data
OUTPUT_FILE = 'created_page_details.json'  # To save the created landing page details

# Configure logging
logging.basicConfig(
    filename='create_landing_page.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log the Access Token (CAUTION: Only do this in a secure environment)
logging.debug(f"Access Token used: {ACCESS_TOKEN}")

# Function to convert ISO 8601 date string to Unix timestamp in milliseconds
def iso_to_unix_timestamp(date_str):
    # Parse the ISO 8601 date string
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    # Return the Unix timestamp in milliseconds
    return int(dt.timestamp() * 1000)

# Function to create a landing page in HubSpot using the payload from JSON file
def create_landing_page():
    # Load payload from the exported JSON file
    with open(EXPORTED_JSON_FILE, 'r') as f:
        payload = json.load(f)
    
    # Remove fields that should not be included in the creation request (e.g., `id`, `createdAt`, etc.)
    payload.pop('id', None)
    payload.pop('createdAt', None)
    payload.pop('updatedAt', None)
    
    # Convert date fields that may need to be in Unix timestamp format
    if 'archivedAt' in payload and isinstance(payload['archivedAt'], str):
        payload['archivedAt'] = iso_to_unix_timestamp(payload['archivedAt'])

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'  # Use Bearer token for OAuth
    }
    
    response = requests.post(CREATE_LANDING_PAGE_URL, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 201:  # 201 indicates successful resource creation
        logging.info("Landing page created successfully")
        page_data = response.json()
        
        # Save the landing page details to a JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(page_data, f, indent=4)
        
        logging.info(f"Landing page details saved to {OUTPUT_FILE}")
        print(f"Landing page created and saved to {OUTPUT_FILE}")
        return page_data
    else:
        logging.error(f"Failed to create landing page: {response.status_code} - {response.text}")
        print(f"Failed to create landing page: {response.status_code} - {response.text}")
        return None

# Main execution
if __name__ == "__main__":
    created_page = create_landing_page()
    if created_page:
        print("Landing page creation successful!")
    else:
        print("Landing page creation failed.")
import requests
import json
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
ACCESS_TOKEN = os.getenv('NP_API_KEY')  # Replace with your HubSpot access token
BASE_API_URL = 'https://api.hubapi.com'
CREATE_LANDING_PAGE_URL = f'{BASE_API_URL}/cms/v3/pages/landing-pages'
EXPORTED_JSON_FILE = 'landing_page_details.json'  # JSON file with the exported page data
OUTPUT_FILE = 'created_page_details.json'  # To save the created landing page details

# Configure logging
logging.basicConfig(
    filename='create_landing_page.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log the Access Token (CAUTION: Only do this in a secure environment)
logging.debug(f"Access Token used: {ACCESS_TOKEN}")

# Function to convert ISO 8601 date string to Unix timestamp in milliseconds
def iso_to_unix_timestamp(date_str):
    # Parse the ISO 8601 date string
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    # Return the Unix timestamp in milliseconds
    return int(dt.timestamp() * 1000)

# Function to create a landing page in HubSpot using the payload from JSON file
def create_landing_page():
    # Load payload from the exported JSON file
    with open(EXPORTED_JSON_FILE, 'r') as f:
        payload = json.load(f)
    
    # Remove fields that should not be included in the creation request (e.g., `id`, `createdAt`, etc.)
    payload.pop('id', None)
    payload.pop('createdAt', None)
    payload.pop('updatedAt', None)
    
    # Convert date fields that may need to be in Unix timestamp format
    if 'archivedAt' in payload and isinstance(payload['archivedAt'], str):
        payload['archivedAt'] = iso_to_unix_timestamp(payload['archivedAt'])

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'  # Use Bearer token for OAuth
    }
    
    response = requests.post(CREATE_LANDING_PAGE_URL, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 201:  # 201 indicates successful resource creation
        logging.info("Landing page created successfully")
        page_data = response.json()
        
        # Save the landing page details to a JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(page_data, f, indent=4)
        
        logging.info(f"Landing page details saved to {OUTPUT_FILE}")
        print(f"Landing page created and saved to {OUTPUT_FILE}")
        return page_data
    else:
        logging.error(f"Failed to create landing page: {response.status_code} - {response.text}")
        print(f"Failed to create landing page: {response.status_code} - {response.text}")
        return None

# Main execution
if __name__ == "__main__":
    created_page = create_landing_page()
    if created_page:
        print("Landing page creation successful!")
    else:
        print("Landing page creation failed.")