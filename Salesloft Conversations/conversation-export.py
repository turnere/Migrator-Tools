import requests
import logging
import json  # For exporting data to JSON
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLMIP_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2'
CONVERSATION_IDS = [
    '35bd7089-933c-4daa-8891-db9649686781'
]

# Configure logging
logging.basicConfig(
    filename='conversation_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch conversation data
def fetch_conversation(conversation_id):
    url = f'{BASE_API_URL}/conversations/{conversation_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching conversation data from {url}")  # Log the request

    response = requests.get(url, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        logging.error(f"Error fetching conversation {conversation_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()  # Parse the response JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Conversation {conversation_id} fetched successfully")
    return data

# Function to transform conversation data into the desired format
def transform_conversation(input_data):
    transformed_data = []

    for conversation in input_data:
        # Extract important information from the conversation
        flattened_conversation = {
            "id": conversation['data']['id'],
            "title": conversation['data'].get('title', ''),
            "participants": conversation['data'].get('participants', []),
            "created_at": conversation['data'].get('created_at', ''),
            "updated_at": conversation['data'].get('updated_at', ''),
            "transcript": conversation['data'].get('transcript', '')  # Assuming there's a transcript field
        }
        transformed_data.append(flattened_conversation)

    return transformed_data

def main():
    all_conversations = []  # List to store all fetched and transformed conversation data

    for conversation_id in CONVERSATION_IDS:
        logging.info(f"Processing conversation ID: {conversation_id}")  # Log the conversation being processed
        conversation_data = fetch_conversation(conversation_id)

        if conversation_data:
            all_conversations.append(conversation_data)
        else:
            logging.info(f"No data found for conversation ID: {conversation_id}")

    # If any conversations were fetched, transform and save them
    if all_conversations:
        # Transform the fetched conversation data
        transformed_data = transform_conversation(all_conversations)
        
        # Save the transformed data to a JSON file
        with open('transformed_conversations.json', 'w') as json_file:
            json.dump(transformed_data, json_file, indent=4)  # Pretty print the JSON
        logging.info("Transformed conversation data saved to transformed_conversations.json")
    else:
        logging.info("No conversation data to save.")

if __name__ == "__main__":
    main()
