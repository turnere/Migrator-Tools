import requests
import logging
import json
import csv
from dotenv import load_dotenv
import os

# Loads the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('MIP_API_KEY')   # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
CSV_FILE = 'mip_form_id.csv'  # Path to the CSV file containing form IDs
OUTPUT_CSV = 'mip_form_fields.csv'  # Output CSV file for form fields
OUTPUT_JSON = 'mip_form_details.json'  # Output JSON file for full form details

# Configure logging
logging.basicConfig(
    filename='fetch_forms.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch form IDs from CSV file
def fetch_form_ids_from_csv(csv_file):
    form_ids = []
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                form_ids.append(row['form_id'])  # Assuming 'form_id' is the column name
    except FileNotFoundError:
        logging.error(f"CSV file {csv_file} not found.")
    except KeyError:
        logging.error(f"'form_id' column not found in the CSV file.")
    return form_ids

# Function to fetch form details
def fetch_form_details(form_id):
    url = f'{BASE_API_URL}/forms/v2/forms/{form_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching form data from {url}")  # Log the URL being fetched
    
    response = requests.get(url, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        logging.error(f"Error fetching form {form_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()  # Attempt to parse JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Form {form_id} fetched successfully")
    return data

# Function to extract field names from form data
def extract_field_names(form_data):
    fields = []
    if 'formFieldGroups' in form_data:
        for group in form_data['formFieldGroups']:
            for field in group['fields']:
                fields.append(field.get('name', 'Unknown'))  # Get field name or 'Unknown' if not present
    return fields

# Function to write field names to CSV
def write_fields_to_csv(form_id, field_names, output_csv):
    try:
        with open(output_csv, 'a', newline='') as file:
            writer = csv.writer(file)
            for field_name in field_names:
                writer.writerow([form_id, field_name])
        logging.info(f"Field names for form {form_id} written to {output_csv}")
    except Exception as e:
        logging.error(f"Error writing to CSV: {e}")

# Function to write form details to JSON as part of a JSON array
def write_form_details_to_json(form_data_list, output_json):
    try:
        # Open the file in write mode and write the entire array at once
        with open(output_json, 'w') as json_file:
            json.dump(form_data_list, json_file, indent=4)  # Write the list as a JSON array with indentation
        logging.info(f"All form data written to {output_json}")
    except Exception as e:
        logging.error(f"Error writing to JSON: {e}")

def main():
    # Initialize the output CSV with headers
    with open(OUTPUT_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['form_id', 'field_name'])

    form_ids = fetch_form_ids_from_csv(CSV_FILE)  # Get form IDs from the CSV file

    if not form_ids:
        logging.error("No form IDs found in CSV. Exiting.")
        return

    form_data_list = []  # List to hold all form data

    for form_id in form_ids:
        logging.info(f"Processing form ID: {form_id}")  # Log the form ID being processed
        form_data = fetch_form_details(form_id)

        if form_data:
            field_names = extract_field_names(form_data)  # Extract field names from form data
            write_fields_to_csv(form_id, field_names, OUTPUT_CSV)  # Write the field names to the CSV
            form_data_list.append(form_data)  # Add form data to the list
        else:
            logging.info(f"No data found for form ID: {form_id}")

    # Write all form data to JSON file as a valid array
    write_form_details_to_json(form_data_list, OUTPUT_JSON)

if __name__ == "__main__":
    main()
