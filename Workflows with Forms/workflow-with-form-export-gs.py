import requests
import logging
import csv
from dotenv import load_dotenv
import os

# Load the .env file into the system environment
load_dotenv()

# Constants
API_KEY = os.getenv('GS_API_KEY')   # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com'
WORKFLOW_IDS_CSV = 'workflow_ids.csv'  # CSV that contains workflow IDs
FORM_IDS_CSV = 'form_ids.csv'  # CSV that contains the form IDs to compare

# Configure logging
logging.basicConfig(
    filename='form_workflow_matching.log',
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

    logging.debug(f"Fetching workflow data from {url}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Error fetching workflow {workflow_id}: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
        return None

    logging.debug(f"Workflow {workflow_id} fetched successfully")
    return data

# Recursive function to extract form IDs from enrollment criteria
def extract_form_ids(workflow_data):
    form_ids = []

    # Ensure the workflow has enrollment criteria with a listFilterBranch
    if 'enrollmentCriteria' in workflow_data and 'listFilterBranch' in workflow_data['enrollmentCriteria']:
        list_filter_branch = workflow_data['enrollmentCriteria']['listFilterBranch']
        
        # Traverse the filterBranches and look for form IDs in filters
        for branch in list_filter_branch.get('filterBranches', []):
            for filter_item in branch.get('filters', []):
                if filter_item.get('filterType') == 'FORM_SUBMISSION' and 'formId' in filter_item:
                    form_ids.append(filter_item['formId'])

    return form_ids

# Function to read workflow IDs from a CSV file
def read_workflow_ids_from_csv(csv_file):
    workflow_ids = []
    try:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    workflow_ids.append(row[0])
    except FileNotFoundError:
        logging.error(f"File {csv_file} not found.")
    return workflow_ids

# Function to read form IDs from a CSV file
def read_form_ids_from_csv(csv_file):
    form_ids = []
    try:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    form_ids.append(row[0])
    except FileNotFoundError:
        logging.error(f"File {csv_file} not found.")
    return form_ids

def main():
    # Step 1: Read form IDs from the CSV file
    form_ids_to_compare = read_form_ids_from_csv(FORM_IDS_CSV)
    if not form_ids_to_compare:
        logging.error("No form IDs found in CSV.")
        return

    # Step 2: Read workflow IDs from the CSV file
    workflow_ids = read_workflow_ids_from_csv(WORKFLOW_IDS_CSV)
    if not workflow_ids:
        logging.error("No workflow IDs found in CSV.")
        return

    # Step 3: Initialize a list to store matching records
    csv_data = []

    # Step 4: Iterate through each workflow and compare form IDs
    for workflow_id in workflow_ids:
        logging.info(f"Processing workflow ID: {workflow_id}")
        workflow_data = fetch_workflow_details(workflow_id)

        if workflow_data:
            workflow_name = workflow_data.get('name', 'Unnamed Workflow')
            form_ids_in_workflow = extract_form_ids(workflow_data)
            
            # Compare the form IDs in the workflow with the provided list of form IDs
            matching_form_ids = [form_id for form_id in form_ids_in_workflow if form_id in form_ids_to_compare]
            
            # If there is a match, append the details to the csv_data
            for form_id in matching_form_ids:
                csv_data.append([workflow_id, workflow_name, form_id])
        else:
            logging.info(f"No data found for workflow ID: {workflow_id}")

    # Step 5: Write the CSV with matching workflow IDs, workflow names, and form IDs
    with open('matching_workflows_forms.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Workflow ID', 'Workflow Name', 'Form ID'])
        writer.writerows(csv_data)

    logging.info("CSV data saved to matching_workflows_forms.csv")

if __name__ == "__main__":
    main()
