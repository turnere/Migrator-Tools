import requests
import csv
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('MIP_API_KEY')  # Replace with your HubSpot API key
BASE_API_URL = 'https://api.hubapi.com/marketing/v3/campaigns/'
CSV_FILE = 'campaign_ids.csv'  # The CSV file containing campaign IDs
OUTPUT_FILE = 'campaigns_export.json'  # The file where campaigns will be written

# Configure logging
logging.basicConfig(
    filename='campaign_import.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch a campaign by its ID
def get_campaign(campaign_id):
    url = f"{BASE_API_URL}{campaign_id}"
    headers = {
        'accept': "application/json",
        'authorization': f"Bearer {API_KEY}"
    }

    # Send GET request to fetch the campaign
    response = requests.get(url, headers=headers)

    # Check for errors
    if response.status_code == 200:
        logging.info(f"Successfully fetched campaign {campaign_id}")
        return response.json()
    else:
        logging.error(f"Failed to fetch campaign {campaign_id}: {response.status_code} - {response.text}")
        return None

def main():
    # List to store all fetched campaigns
    campaigns_data = []

    # Read the CSV file containing campaign IDs
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            campaign_id = row[0]
            campaign_data = get_campaign(campaign_id)
            if campaign_data:
                campaigns_data.append(campaign_data)
                print(f"Successfully fetched campaign {campaign_id}")
            else:
                print(f"Failed to fetch campaign {campaign_id}")

    # Write all fetched campaign data to a JSON file
    with open(OUTPUT_FILE, 'w') as jsonfile:
        json.dump(campaigns_data, jsonfile, indent=4)
        logging.info(f"All campaigns written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
