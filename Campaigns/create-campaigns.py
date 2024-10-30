import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
API_KEY_NEW_INSTANCE = os.getenv('NP_API_KEY')  # Replace with your API key for the new HubSpot instance
BASE_API_URL = 'https://api.hubapi.com/marketing/v3/campaigns/'
JSON_FILE = 'campaigns_export.json'  # The JSON file containing the exported campaigns

# Configure logging
logging.basicConfig(
    filename='campaign_creation.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to create a campaign in the new instance
def create_campaign(campaign_data):
    url = BASE_API_URL
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {API_KEY_NEW_INSTANCE}"
    }
    
    # Extract the necessary fields for the payload
    payload = {
        "name": campaign_data.get("name"),
        "startDate": campaign_data.get("startDate"),
        "endDate": campaign_data.get("endDate"),
        "type": campaign_data.get("type"),
        "status": campaign_data.get("status")
    }

    # Convert the payload to a JSON string
    payload_json = json.dumps(payload)

    # Send POST request to create the campaign
    response = requests.post(url, data=payload_json, headers=headers)

    # Check for errors
    if response.status_code == 201:
        logging.info(f"Successfully created campaign: {campaign_data.get('name')}")
        print(f"Successfully created campaign: {campaign_data.get('name')}")
    else:
        logging.error(f"Failed to create campaign: {campaign_data.get('name')} - {response.status_code} - {response.text}")
        print(f"Failed to create campaign: {campaign_data.get('name')} - {response.status_code} - {response.text}")

def main():
    # Load campaigns data from the JSON file
    with open(JSON_FILE, 'r') as jsonfile:
        campaigns_data = json.load(jsonfile)
    
    # Iterate over each campaign and create it in the new instance
    for campaign_data in campaigns_data:
        create_campaign(campaign_data)

if __name__ == "__main__":
    main()
