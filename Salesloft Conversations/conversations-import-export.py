import requests
import logging
import json
import csv
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLMIP_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_CONVERSATIONS_URL = 'https://api.salesloft.com/v2/conversations'
BASE_API_CALLS_URL = 'https://api.salesloft.com/v2/activities/calls'
PAGE_SIZE = 10  # Adjust the page size to 10 to fetch only 10 conversations for testing

# Configure logging
logging.basicConfig(
    filename='conversation_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch a limited number of conversations
def fetch_limited_conversations(limit=10):
    conversations = []
    page = 1

    while len(conversations) < limit:
        url = f'{BASE_API_CONVERSATIONS_URL}?per_page={PAGE_SIZE}&page={page}'
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

        # Stop fetching more if we reach the limit
        if len(conversations) >= limit:
            conversations = conversations[:limit]  # Trim any extra conversations if over the limit
            break

        # Check if there are more pages
        if 'next_page' not in data['metadata']['paging'] or data['metadata']['paging']['next_page'] is None:
            break  # Exit the loop if there are no more pages

        page += 1  # Move to the next page

    logging.debug(f"Fetched {len(conversations)} conversations successfully")
    return conversations

# Function to fetch call data using call_id
def fetch_call_data(call_id):
    url = f'{BASE_API_CALLS_URL}/{call_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching call data from {url}")  # Log the request

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Error fetching call data: {response.status_code} - {response.text}")
        return None

    try:
        call_data = response.json()  # Parse the response JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Call data for {call_id} fetched successfully")
    return call_data

# Function to extract data from conversations and calls for CSV
def extract_conversation_and_call_data(conversation):
    call_id = conversation.get('call_id', 'Unknown')
    
    # Fetch call data using call_id
    call_data = fetch_call_data(call_id)
    
    if not call_data:
        logging.warning(f"No call data found for call_id: {call_id}")
        return None
    
    # Extract required fields from call data
    call_recording = call_data.get('recordings', [{}])[0].get('_href', '')
    direction = call_data.get('direction', 'Unknown')
    to_phone = call_data.get('to', 'Unknown')
    from_phone = call_data.get('from', 'Unknown')
    duration = call_data.get('duration', 0)
    call_created_at = call_data.get('created_at', '')
    user_guid = call_data.get('user_guid', '')

    # Compile all data into a dictionary for CSV
    compiled_data = {
        "to": to_phone,
        "from": from_phone,
        "duration": duration,
        "call_created_at": call_created_at,
        "user_guid": user_guid,
        "direction": direction,
        "recording": call_recording
    }

    logging.debug(f"Extracted conversation and call data: {compiled_data}")
    return compiled_data

# Function to export extracted call data to a CSV file
def export_to_csv(call_data_list, filename='call_data.csv'):
    # Define CSV headers
    headers = ['to', 'from', 'duration', 'call_created_at', 'user_guid', 'direction', 'recording']
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write header
        writer.writeheader()
        
        # Write rows
        for call_data in call_data_list:
            if call_data:
                writer.writerow(call_data)

    logging.info(f"Call data successfully exported to {filename}")

def main():
    logging.info("Starting conversation export to CSV...")

    # Fetch a limited number of conversations
    conversations = fetch_limited_conversations(limit=10)

    if conversations:
        # Extract conversation and call data for each conversation
        call_data_list = [extract_conversation_and_call_data(conversation) for conversation in conversations]
        
        # Export the extracted call data to CSV
        export_to_csv(call_data_list)
        
        logging.info(f"Process completed, total conversations processed: {len(conversations)}")
    else:
        logging.info("No conversation data to process.")

if __name__ == "__main__":
    main()
