import os
from hubspot import HubSpot
from hubspot.crm.contacts import ApiException
import requests

# Function to query HubDB and find the corresponding cmo_source using form_id
def get_cmo_source_from_hubdb(access_token, form_id):
    # HubDB table ID for the lookup
    hubdb_table_id = '25912124'
    hubdb_url = f"https://api.hubapi.com/cms/v3/hubdb/tables/{hubdb_table_id}/rows"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(hubdb_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve HubDB table. Status code: {response.status_code}")

    hubdb_data = response.json().get('results', [])

    # Search for the cmo_source based on the form_id
    for row in hubdb_data:
        row_values = row.get('values', {})
        
        # Assuming 'form_id' and 'cmo_source' are column names in your HubDB table
        if row_values.get('form_id') == form_id:
            cmo_source_data = row_values.get('cmo_source')
            
            # No need to parse, cmo_source_data is already a dict
            if cmo_source_data and isinstance(cmo_source_data, dict):
                return cmo_source_data.get('name')  # Return only the 'name' field

    return None  # Return None if no matching cmo_source is found

def main(event):
    # Ensure that SECRET_NAME contains a valid OAuth access token
    access_token = os.getenv('secretApp')

    if not access_token:
        return {
            "outputFields": {
                "error": "Authentication token not found. Ensure 'SECRET_NAME' is set with a valid OAuth token."
            }
        }

    # Instantiate HubSpot client with OAuth token
    hubspot = HubSpot(access_token=access_token)

    phone = ''
    try:
        # Retrieve the contact's phone number using the contact ID from the event
        contact_id = event.get('object').get('objectId')
        ApiResponse = hubspot.crm.contacts.basic_api.get_by_id(contact_id, properties=["phone"])
        phone = ApiResponse.properties.get('phone')
    except ApiException as e:
        print(f"Error fetching contact phone number: {e}")
        raise

    # Get email and recent conversion event name from the input fields
    email = event.get('inputFields').get('email')
    recent_conversion_event_name = event.get('inputFields').get('recent_conversion_event_name')

    if not recent_conversion_event_name:
        return {
            "outputFields": {
                "error": "No recent conversion event name found."
            }
        }

    # Define HubSpot Forms API settings with OAuth token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Step 1: Get all forms from HubSpot Forms API using the token from secrets
    forms_url = "https://api.hubapi.com/forms/v2/forms"
    response = requests.get(forms_url, headers=headers)

    if response.status_code != 200:
        return {
            "outputFields": {
                "error": f"Failed to retrieve forms. Status code: {response.status_code}",
                "response": response.json()
            }
        }

    forms_data = response.json()

    # Step 2: Search for the form with a name matching the recent conversion event name
    matching_form = None
    for form in forms_data:
        if form.get("name") == recent_conversion_event_name:
            matching_form = form
            break

    if not matching_form:
        return {
            "outputFields": {
                "error": "No matching form found for the recent conversion event name."
            }
        }

    form_id = matching_form.get("guid")  # Form ID is stored in the 'guid' field

    # Step 3: Use the form_id to get the corresponding cmo_source from HubDB
    cmo_source = get_cmo_source_from_hubdb(access_token, form_id)

    if not cmo_source:
        return {
            "outputFields": {
                "error": "No matching cmo_source found in HubDB for the form_id."
            }
        }

    # Step 4: Check if cmo_source is 'demo_request' and set latest_cmo_source accordingly
    latest_cmo_source = None
    if cmo_source == "demo_request":
        latest_cmo_source = "Demo Request"
    else:
        latest_cmo_source = cmo_source  # Default to the original cmo_source name

    # Return the email, phone, form ID, cmo_source (name), and latest_cmo_source in the output fields
    return {
        "outputFields": {
            "email": email,
            "phone": phone,
            "form_id": form_id,
            "cmo_source": cmo_source,  # This is the 'name' field from the cmo_source
            "latest_cmo_source": latest_cmo_source,  # This will be 'Demo Request' if the cmo_source is 'demo_request'
            "form_name": recent_conversion_event_name
        }
    }
