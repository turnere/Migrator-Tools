import requests
import logging
import json  # For exporting data to JSON
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLMIP_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2/conversations'
PAGE_SIZE = 50  # Adjust this if needed (default for SalesLoft API is 50)

# Configure logging
logging.basicConfig(
    filename='conversation_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch all conversations with pagination
def fetch_all_conversations():
    conversations = []
    page = 1

    while True:
        url = f'{BASE_API_URL}?per_page={PAGE_SIZE}&page={page}'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }

        logging.debug(f"Fetching conversations from {url}")  # Log the request

        response = requests.get(url, headers=headers)

        # Check for HTTP errors
        if response.status_code != 200:
            logging.error(f"Error fetching conversations: {response.status_code} - {response.text}")
            return None

        try:
            data = response.json()  # Parse the response JSON
        except requests.exceptions.JSONDecodeError:
            logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
            return None

        conversations.extend(data['data'])  # Add current page data to conversations list

        # Check if there are more pages
        if 'next_page' in data['metadata']['paging'] and data['metadata']['paging']['next_page'] is not None:
            page += 1  # Move to the next page
        else:
            break  # Exit the loop if there are no more pages

    logging.debug(f"All conversations fetched successfully, total: {len(conversations)}")
    return conversations

def main():
    logging.info("Starting conversation export...")

    # Fetch all conversations with pagination
    conversations = fetch_all_conversations()

    if conversations:
        # Save the full JSON data to a file
        with open('full_conversations.json', 'w') as json_file:
            json.dump(conversations, json_file, indent=4)  # Pretty print the JSON
        logging.info(f"Full conversation data saved to full_conversations.json, total: {len(conversations)}")
    else:
        logging.info("No conversation data to save.")

if __name__ == "__main__":
    main()
