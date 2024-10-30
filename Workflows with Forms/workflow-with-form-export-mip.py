import requests
import logging
import json
import csv  # Import CSV library for reading and writing CSV files
from dotenv import load_dotenv
import os

# Loads the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('MIP_API_KEY')   # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'  # Base URL for HubSpot API
WORKFLOW_IDS_CSV = 'workflow_ids.csv'  # The CSV file containing workflow IDs

# Configure logging
logging.basicConfig(
    filename='fetch_workflow_and_forms.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to fetch workflow details
def fetch_workflow_details(workflow_id):
    url = f'{BASE_API_URL}/automation/v4/flows/{workflow_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    logging.debug(f"Fetching workflow data from {url}")  # Log the URL being fetched
    response = requests.get(url, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        logging.error(f"Error fetching workflow {workflow_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()  # Attempt to parse JSON
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Workflow {workflow_id} fetched successfully")
    return data

# Recursive function to extract formIds from the nested enrollment criteria
def extract_form_ids_from_branch(branch):
    form_ids = []
    if 'filters' in branch:
        for filter_item in branch['filters']:
            if 'formId' in filter_item:
                form_ids.append(filter_item['formId'])
    
    if 'filterBranches' in branch:
        for sub_branch in branch['filterBranches']:
            form_ids.extend(extract_form_ids_from_branch(sub_branch))  # Recursively search sub-branches
    
    return form_ids

# Function to extract formIds from the enrollment criteria in workflow data
def extract_form_ids(workflow_data):
    form_ids = []
    if 'enrollmentCriteria' in workflow_data and 'listFilterBranch' in workflow_data['enrollmentCriteria']:
        main_branch = workflow_data['enrollmentCriteria']['listFilterBranch']
        form_ids = extract_form_ids_from_branch(main_branch)
    return form_ids

# Function to fetch form details using the forms API
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

# Function to read workflow IDs from a CSV file
def read_workflow_ids_from_csv(csv_file):
    workflow_ids = []
    try:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if the row is not empty
                    workflow_ids.append(row[0])  # Assuming the workflow ID is in the first column
    except FileNotFoundError:
        logging.error(f"File {csv_file} not found.")
    return workflow_ids

def main():
    csv_data = []  # List to store CSV rows (workflow ID, workflow name, form ID, form name)

    # Read workflow IDs from the CSV file
    workflow_ids = read_workflow_ids_from_csv(WORKFLOW_IDS_CSV)

    if not workflow_ids:
        logging.error("No workflow IDs found.")
        return

    for workflow_id in workflow_ids:
        logging.info(f"Processing workflow ID: {workflow_id}")  # Log the workflow ID being processed
        workflow_data = fetch_workflow_details(workflow_id)

        if workflow_data:
            # Extract the name and formId(s) from the workflow
            workflow_name = workflow_data.get('name', 'Unnamed Workflow')
            form_ids = extract_form_ids(workflow_data)
            
            if form_ids:
                for form_id in form_ids:
                    # Fetch additional form details (name)
                    form_data = fetch_form_details(form_id)
                    if form_data:
                        form_name = form_data.get('name', 'Unknown Form Name')
                        # Add workflow ID, workflow name, form ID, and form name to the CSV data
                        csv_data.append([workflow_id, workflow_name, form_id, form_name])
                    else:
                        csv_data.append([workflow_id, workflow_name, form_id, 'Unknown Form Name'])
            else:
                # If no formId is found, still log the workflow ID and name
                csv_data.append([workflow_id, workflow_name, 'No formId found', 'N/A'])

        else:
            logging.info(f"No data found for workflow ID: {workflow_id}")

    # Write the CSV file with workflow ID, workflow name, form ID, and form name
    with open('workflow_formIds_forms.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Workflow ID', 'Workflow Name', 'Form ID', 'Form Name'])  # Write header row
        writer.writerows(csv_data)  # Write data rows

    logging.info("CSV data saved to workflow_formIds_forms.csv")

if __name__ == "__main__":
    main()
