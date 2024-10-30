import requests
import json
import os
import csv
from dotenv import load_dotenv

# Loads the .env file into the system environment
load_dotenv()

# Fetch the API key from environment variables
API_KEY = os.getenv('GS_API_KEY')  # Ensure that 'GS_API_KEY' is set in your environment

if API_KEY is None:
    print("API key not found. Please set the 'GS_API_KEY' environment variable.")
    exit()

# The CSV file containing workflow IDs
WORKFLOW_IDS_CSV = 'workflow_ids.csv'  # Path to your CSV file

# Function to fetch workflow details from HubSpot
def fetch_workflow_details(workflow_id):
    url = f"https://api.hubapi.com/automation/v4/flows/{workflow_id}"
    
    headers = {
        'accept': "application/json",
        'authorization': f"Bearer {API_KEY}"  # Use the API key retrieved from the environment
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch workflow {workflow_id}. Status code: {response.status_code}")
        return None

# Read the workflow IDs from the CSV file
with open(WORKFLOW_IDS_CSV, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    workflows = {}
    for row in csv_reader:
        workflow_id = row['workflow_id']  # Assuming the CSV has a column 'workflow_id'
        
        # Fetch workflow details
        workflow_data = fetch_workflow_details(workflow_id)
        
        if workflow_data:
            workflows[workflow_id] = workflow_data

# Save all workflow details to a single JSON file
with open('hubspot_workflows.json', 'w') as json_file:
    json.dump(workflows, json_file, indent=4)

print("HubSpot workflow details saved to hubspot_workflows.json")
