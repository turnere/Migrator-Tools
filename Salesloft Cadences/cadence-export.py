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
CADENCE_IDS = [
    '654913'
]

# Configure logging
logging.basicConfig(
    filename='cadence_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch cadence export data
def fetch_cadence_export(cadence_id):
    url = f'{BASE_API_URL}/cadence_exports/{cadence_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching cadence export data from {url}")  # Log the request

    response = requests.get(url, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        logging.error(f"Error fetching cadence {cadence_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()  # Parse the response JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Cadence {cadence_id} fetched successfully")
    return data

# Function to transform cadence export data into the desired format
def transform_cadence(input_data):
    transformed_data = []

    for cadence in input_data:
        # Flatten the structure
        data = cadence['data']['cadence_content']
        flattened_cadence = {
            "settings": {
                "name": data['settings']['name'],  # Existing
                "target_daily_people": data['settings'].get('target_daily_people', 10),  # Default 10
                "remove_replied": data['settings'].get('remove_replied', True),
                "remove_bounced": data['settings'].get('remove_bounced', True),
                "reschedule_from_pause_enabled": data['settings'].get('reschedule_from_pause_enabled', True),
                "external_identifier": data['settings'].get('external_identifier', None),
                "cadence_function": data['settings'].get('cadence_function', 'outbound'),
                "added_stage_setting": data['settings'].get('added_stage_setting', 'Open'),
                "bounced_stage_setting": data['settings'].get('bounced_stage_setting', 'Working'),
                "finished_stage_setting": data['settings'].get('finished_stage_setting', 'Completed'),
                "replied_stage_setting": data['settings'].get('replied_stage_setting', 'Do Not Contact'),
            },
            "sharing_settings": {
                "team_cadence": data['sharing_settings'].get('team_cadence', False),
                "shared": data['sharing_settings'].get('team_cadence', False)
            },
            "cadence_content": {
                "step_groups": []
            }
        }

        # Iterate over step_groups and steps, and simplify them
        for step_group in data['step_groups']:
            automated_settings = step_group.get('automated_settings', {})
            if step_group.get('automated', False):
                send_type = automated_settings.get('send_type', 'after_time_delay')

                # Handle `send_type` conditions properly
                if send_type == 'after_time_delay':
                    # Remove `time_of_day` and `timezone_mode` for `after_time_delay`, include `delay_time`
                    automated_settings.pop('time_of_day', None)
                    automated_settings.pop('timezone_mode', None)
                    automated_settings['delay_time'] = automated_settings.get('delay_time', 0)  # Ensure delay_time is present
                elif send_type == 'at_time':
                    # Include `time_of_day` and `timezone_mode` for `at_time`, remove `delay_time`
                    automated_settings['time_of_day'] = automated_settings.get('time_of_day', '08:00')  # Default time
                    automated_settings['timezone_mode'] = automated_settings.get('timezone_mode', 'user')  # Default timezone mode
                    automated_settings.pop('delay_time', None)  # Remove delay_time for at_time

            simplified_step_group = {
                "day": step_group['day'],
                "due_immediately": step_group.get('due_immediately', False),
                "automated": step_group.get('automated', False),
                "reference_id": step_group.get('reference_id'),
                "automated_settings": automated_settings,
                "steps": []
            }

            for step in step_group['steps']:
                simplified_step = {
                    "name": step['name'],
                    "enabled": step['enabled'],
                    "type": step['type'],
                    "type_settings": step['type_settings']
                }
                simplified_step_group['steps'].append(simplified_step)

            flattened_cadence["cadence_content"]["step_groups"].append(simplified_step_group)

        transformed_data.append(flattened_cadence)

    return transformed_data



def main():
    all_cadence_exports = []  # List to store all fetched and transformed cadence export data

    for cadence_id in CADENCE_IDS:
        logging.info(f"Processing cadence ID: {cadence_id}")  # Log the cadence being processed
        cadence_data = fetch_cadence_export(cadence_id)

        if cadence_data:
            all_cadence_exports.append(cadence_data)
        else:
            logging.info(f"No data found for cadence ID: {cadence_id}")

    # If any cadences were fetched, transform and save them
    if all_cadence_exports:
        # Transform the fetched cadence data
        transformed_data = transform_cadence(all_cadence_exports)
        
        # Save the transformed data to a JSON file
        with open('transformed_cadence_exports.json', 'w') as json_file:
            json.dump(transformed_data, json_file, indent=4)  # Pretty print the JSON
        logging.info("Transformed cadence export data saved to transformed_cadence_exports.json")
    else:
        logging.info("No cadence data to save.")

if __name__ == "__main__":
    main()
