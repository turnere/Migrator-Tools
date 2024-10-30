import requests
import json
import os
from dotenv import load_dotenv

# Loads the .env file into the system environment
load_dotenv()

# Fetch the API key for the new HubSpot instance from environment variables
API_KEY_NEW_INSTANCE = os.getenv('NPSB_API_KEY')  # Ensure that 'NPSB_API_KEY' is set in your environment

if API_KEY_NEW_INSTANCE is None:
    print("API key not found for the new instance. Please set the 'NPSB_API_KEY' environment variable.")
    exit()

# The URL to create a new workflow
url = "https://api.hubapi.com/automation/v4/flows"

# Load the workflow data from the JSON file
with open('hubspot_workflows.json', 'r') as json_file:
    workflows = json.load(json_file)

# Define supported actionTypeIds
supported_action_type_ids = [
    "0-35", "0-1", "0-13", "0-4", "0-8", "0-9", "0-5", "0-3", "0-14"
]

# Function to adjust actions and only include supported actionTypeIds
def adjust_actions(actions):
    adjusted_actions = []
    previous_action_id = None  # Track the previous action to handle skipping

    for index, action in enumerate(actions):
        action_type_id = action.get("actionTypeId")

        # Skip actions with unsupported actionTypeIds
        if action_type_id not in supported_action_type_ids:
            print(f"Skipping unsupported actionTypeId: {action_type_id}, actionId {action.get('actionId')}")
            continue

        # Get the nextActionId if it exists
        next_action_id = action.get('connection', {}).get('nextActionId')

        # If the previous action exists and the current action is valid, ensure continuity of nextActionId
        if previous_action_id is not None:
            adjusted_actions[-1]['connection']['nextActionId'] = action.get('actionId')
            print(f"Set nextActionId {action.get('actionId')} for previous actionId {previous_action_id}.")

        # Build the adjusted action object
        adjusted_action = {
            "actionId": action.get("actionId"),
            "type": action.get("type"),
            "actionTypeVersion": action.get("actionTypeVersion", 0),
            "actionTypeId": action.get("actionTypeId"),
            "fields": action.get("fields", {}),
            "connection": {
                "edgeType": action.get("connection", {}).get("edgeType", "STANDARD"),
                "nextActionId": next_action_id  # Use only if explicitly defined
            } if next_action_id else {"edgeType": "STANDARD"}  # Handle the last action or actions without nextActionId
        }

        adjusted_actions.append(adjusted_action)
        previous_action_id = action.get('actionId')  # Set the current action as the previous action for next iteration

    return adjusted_actions

# Function to create a new workflow in the new instance
def create_workflow_with_enrollment_and_actions(workflow_data):
    # Prepare the payload with the necessary fields including enrollment criteria and actions
    payload = {
        "type": "CONTACT_FLOW",
        "objectTypeId": "0-1",  # Assuming this is correct for contact-based workflows
        "isEnabled": True,
        "flowType": "WORKFLOW",
        "name": f"Copy of {workflow_data['name']}",
        "description": workflow_data.get("description", "Created via API"),
        "enrollmentCriteria": workflow_data.get("enrollmentCriteria", {}),
        "actions": adjust_actions(workflow_data.get('actions', []))  # Process actions before including
    }

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {API_KEY_NEW_INSTANCE}"
    }

    # Convert the payload to a JSON string
    payload_json = json.dumps(payload)
    
    # Send the POST request to create the new workflow
    response = requests.post(url, data=payload_json, headers=headers)
    
    if response.status_code == 201:
        print(f"Successfully created workflow: {workflow_data['name']}")
    else:
        print(f"Failed to create workflow: {workflow_data['name']}. Status code: {response.status_code}")
        print(response.text)

# Iterate over each workflow and create it in the new instance
for workflow_id, workflow_data in workflows.items():
    create_workflow_with_enrollment_and_actions(workflow_data)
