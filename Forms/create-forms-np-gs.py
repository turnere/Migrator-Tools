import requests
import json
import logging
import os
import csv
from dotenv import load_dotenv

# Loads the .env file into the system environment
load_dotenv()

# Constants
API_KEY_NEW_INSTANCE = os.getenv('NP_API_KEY')  # Replace with your new HubSpot account's API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
JSON_FILE = 'gs_form_details.json'  # Path to the JSON file with form data
CSV_FILE = 'field_mappings.csv'  # Path to the CSV file with the mappings

# Configure logging
logging.basicConfig(
    filename='create_forms.log',
    level=logging.DEBUG,  # Change to DEBUG to log everything, or INFO for general logging
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_field_mappings(csv_file):
    field_mappings = {}
    with open(csv_file, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row:  # Check for empty rows
                logging.warning("Encountered empty row in CSV.")
                continue
            try:
                external_name = row['external_name'].strip()  # Strip any extra spaces
                internal_name = row['gs_internal_name'].strip()
                field_mappings[external_name] = internal_name
            except KeyError as e:
                logging.error(f"Missing expected key in row: {row}. Error: {e}")
    logging.info(f"Loaded {len(field_mappings)} field mappings from CSV.")
    return field_mappings

def clean_form_data(form_data, field_mappings):
    # Remove unnecessary fields as before
    fields_to_remove = [
        'guid', 'createdAt', 'updatedAt', 'performableHtml', 'migratedFrom',
        'tmsId', 'campaignGuid', 'parentId', 'deletable', 'deletedAt',
        'isPublished', 'publishAt', 'unpublishAt', 'publishedAt', 'customUid',
        'editVersion', 'thankYouMessageJson', 'internalUpdatedAt', 'portableKey',
        'embedVersion', 'isSmartGroup', 'richText'
    ]
    
    for field in fields_to_remove:
        form_data.pop(field, None)

    # Clean up metaData fields as well, if necessary
    if 'metaData' in form_data:
        form_data['metaData'] = [meta for meta in form_data['metaData'] if meta.get('name') != 'createdByAppId']

    # List of fields to skip due to validation errors
    fields_to_skip = [
        'leadsource', 'website_url_earthnet', 'website_url_msn', 'website_url_cox',
        'website_url_ymail', 'website_url_bellsouth', 'website_url_rocketmail',
        'website_url_yahoo', 'website_url_charter', 'website_url_comcast',
        'website_url_outlook', 'website_url_hotmail', 'website_url_aol',
        'website_url_juno', 'website_url_gmx', 'website_url_mac', 
        'website_url_attnet', 'website_url_me', 'website_url_sbcglobal',
        'lead_source_salesforce_', 'lifecyclestage'
    ]

    def remove_skipped_fields(fields):
        """Helper function to remove skipped fields from a list of fields."""
        return [field for field in fields if field.get('name').strip() not in [name.strip() for name in fields_to_skip]]

    def replace_field_names(fields):
        """Replace internal field names with external field names based on the mappings."""
        for field in fields:
            internal_name = field.get('name')
            # Check if the field name exists in the mappings
            if internal_name in field_mappings.values():
                # Find the corresponding external name in the mappings
                for external_name, mapped_internal_name in field_mappings.items():
                    if internal_name == mapped_internal_name:
                        logging.debug(f"Replacing field name '{internal_name}' with '{external_name}'")
                        field['name'] = external_name
                        break

    def clean_field_group(field_group):
        """Recursively clean fields and dependent fields."""
        # First, remove fields directly in the field group
        field_group['fields'] = remove_skipped_fields(field_group.get('fields', []))
        
        # Replace internal field names with external field names
        replace_field_names(field_group['fields'])

        # Now, handle nested 'dependentFormField' if it exists
        for field in field_group['fields']:
            if 'dependentFormField' in field:
                dependent_field = field['dependentFormField']
                logging.debug(f"Cleaning dependent form field: {dependent_field.get('name')}")
                
                # Clean the dependent fields
                if dependent_field.get('name') in fields_to_skip:
                    logging.info(f"Skipping dependent form field: {dependent_field.get('name')}")
                    field.pop('dependentFormField')  # Remove the dependent form field if it should be skipped
                else:
                    # Recursively clean inside dependent fields as well
                    clean_field_group({'fields': [dependent_field]})

    # Clean fields and dependent fields in all field groups
    if 'formFieldGroups' in form_data:
        for field_group in form_data['formFieldGroups']:
            clean_field_group(field_group)
    
    logging.debug(f"Cleaned form data: {form_data.get('name', 'Unnamed Form')}")
    return form_data

def create_form(form_data, max_retries=3):
    url = f'{BASE_API_URL}/forms/v2/forms'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY_NEW_INSTANCE}'
    }
    
    for attempt in range(max_retries):
        logging.info(f"Attempting to create form: {form_data.get('name', 'Unnamed Form')} (Attempt {attempt + 1})")
        response = requests.post(url, headers=headers, json=form_data)

        if response.status_code == 201:
            logging.info(f"Successfully created form: {form_data.get('name', 'Unnamed Form')}")
            return response.json()
        elif response.status_code == 409:  # Conflict, likely due to duplicate form
            logging.error(f"Form already exists: {form_data.get('name', 'Unnamed Form')} - Response: {response.text}")
            return None
        elif response.status_code == 400:  # Bad request, log the response
            try:
                error_response = response.json()
                logging.error(f"Bad request when creating form: {form_data.get('name', 'Unnamed Form')} - {error_response}")
            except requests.exceptions.JSONDecodeError:
                logging.error(f"Failed to parse JSON response. Response text: {response.text}")
            return None
        elif response.status_code != 200:
            logging.error(f"Failed to create form. Status code: {response.status_code}, Response: {response.text}")
    
    return None


def main():
    # Load the field mappings from the CSV file
    field_mappings = load_field_mappings(CSV_FILE)

    # Read the exported form data from the JSON file
    with open(JSON_FILE, 'r') as file:
        forms_data = json.load(file)

    # Log the number of forms found in the JSON file
    logging.info(f"Found {len(forms_data)} forms in the JSON file.")

    # Iterate over the list of forms in case there are multiple forms in the file
    for form_data in forms_data:
        # Clean the form data and rename fields based on CSV mappings
        cleaned_data = clean_form_data(form_data, field_mappings)
        
        # Create the form in the new HubSpot instance
        create_form(cleaned_data)

if __name__ == "__main__":
    main()
