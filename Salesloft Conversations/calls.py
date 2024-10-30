import requests
import logging
import csv
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv('SLMIP_API_KEY')  # Replace with your SalesLoft API key from .env
BASE_API_URL = 'https://api.salesloft.com/v2/activities/calls'
MAX_CALLS = 10  # Limit to 10 calls for testing
PAGE_SIZE = 10  # We will set this to 10 to limit the results to 10 calls in one request

# Configure logging
logging.basicConfig(
    filename='call_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch calls with a limit of 10
def fetch_limited_calls():
    calls = []
    page = 1

    while len(calls) < MAX_CALLS:
        url = f'{BASE_API_URL}?per_page={PAGE_SIZE}&page={page}'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }

        logging.debug(f"Fetching calls from {url}")  # Log the request

        response = requests.get(url, headers=headers)

        # Check for HTTP errors
        if response.status_code != 200:
            logging.error(f"Error fetching calls: {response.status_code} - {response.text}")
            return None

        try:
            data = response.json()  # Parse the response JSON
        except requests.exceptions.JSONDecodeError:
            logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
            return None

        calls.extend(data['data'])  # Add current page data to calls list

        # If we have fetched the desired number of calls, stop
        if len(calls) >= MAX_CALLS:
            calls = calls[:MAX_CALLS]  # Trim excess if we fetched more than needed
            break

        # Check if there are more pages, if not, exit the loop
        if 'next_page' not in data['metadata']['paging'] or data['metadata']['paging']['next_page'] is None:
            break  # No more pages to fetch

        page += 1  # Move to the next page

    logging.debug(f"Fetched {len(calls)} calls successfully.")
    return calls

# Function to extract relevant data for CSV
# Function to extract relevant data for CSV
def extract_call_data(call):
    return {
        "id": call.get('id', ''),
        "to": call.get('to', ''),
        "duration": call.get('duration', 0),
        "sentiment": call.get('sentiment', ''),
        "disposition": call.get('disposition', ''),
        "created_at": call.get('created_at', ''),
        "updated_at": call.get('updated_at', ''),
        "recordings": [recording.get('_href', '') for recording in call.get('recordings', [])],  # Extract recording URLs
        "user": call.get('user', {}).get('id', 'Unknown'),  # Safeguard for missing user information
        "action": call.get('action', {}).get('id', 'Unknown') if call.get('action') else 'Unknown',  # Handle None
        "task": call.get('task', {}).get('id', 'Unknown') if call.get('task') else 'Unknown',  # Handle None
        "called_person": call.get('called_person', {}).get('id', 'Unknown') if call.get('called_person') else 'Unknown',  # Handle None
        "crm_activity": call.get('crm_activity', {}).get('id', 'Unknown') if call.get('crm_activity') else 'Unknown',  # Handle None
        "note": call.get('note', {}).get('id', 'Unknown') if call.get('note') else 'Unknown',  # Handle None
        "cadence": call.get('cadence', {}).get('id', 'Unknown') if call.get('cadence') else 'Unknown',  # Handle None
        "step": call.get('step', {}).get('id', 'Unknown') if call.get('step') else 'Unknown'  # Handle None
    }


# Function to export extracted call data to a CSV file
def export_to_csv(call_data_list, filename='call_data.csv'):
    # Define CSV headers
    headers = ['id', 'to', 'duration', 'sentiment', 'disposition', 'created_at', 'updated_at', 'recordings', 
               'user', 'action', 'task', 'called_person', 'crm_activity', 'note', 'cadence', 'step']
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write header
        writer.writeheader()
        
        # Write rows
        for call_data in call_data_list:
            writer.writerow(call_data)

    logging.info(f"Call data successfully exported to {filename}")

# Function to log the raw calls data to a JSON file
def log_raw_data_to_json(raw_data, filename='raw_call_data.json'):
    with open(filename, 'w') as json_file:
        json.dump(raw_data, json_file, indent=4)
    logging.info(f"Raw call data successfully logged to {filename}")

def main():
    logging.info("Starting call export to CSV and logging raw data to JSON...")

    # Fetch a limited number of calls
    calls = fetch_limited_calls()

    if calls:
        # Log the raw call data to a JSON file
        log_raw_data_to_json(calls)

        # Extract call data for each call
        call_data_list = [extract_call_data(call) for call in calls]
        
        # Export the extracted call data to CSV
        export_to_csv(call_data_list)
        
        logging.info(f"Process completed, total calls processed: {len(calls)}")
    else:
        logging.info("No call data to process.")

if __name__ == "__main__":
    main()
