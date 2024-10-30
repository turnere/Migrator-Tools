import os
from hubspot import HubSpot
from hubspot.crm.contacts import ApiException
import requests

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

    # Return the email, phone, and form ID in the output fields
    return {
        "outputFields": {
            "email": email,
            "phone": phone,
            "form_id": form_id,
            "form_name": recent_conversion_event_name
        }
    }
