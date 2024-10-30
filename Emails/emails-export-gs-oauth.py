import requests
import json
import logging
import os
from dotenv import load_dotenv
from flask import Flask, request, redirect

app = Flask(__name__)
load_dotenv()

# Constants
CLIENT_ID = os.getenv('GS_ID')
CLIENT_SECRET = os.getenv('GS_SECRET')
REDIRECT_URI = os.getenv('GS_REDIRECT')
SCOPES = 'contacts content marketing'
AUTH_URL = 'https://app.hubspot.com/oauth/authorize'
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
BASE_API_URL = 'https://api.hubapi.com'
EMAIL_ID = '178358237455'  # Replace with the email ID you want to export
OUTPUT_FILE = 'email_details.json'  # File to save the exported email details

# Configure logging
logging.basicConfig(
    filename='email_export.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def login():
    # Step 1: Redirect the user to the HubSpot OAuth authorization URL
    auth_url = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)


@app.route('/oauth/callback')
def oauth_callback():
    # Step 2: Handle the OAuth callback and exchange the authorization code for an access token
    auth_code = request.args.get('code')
    
    if not auth_code:
        return "Authorization code not found", 400

    # Exchange the authorization code for an access token
    token_response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': auth_code
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    if token_response.status_code != 200:
        logging.error(f"Failed to get access token: {token_response.text}")
        return "Failed to get access token", 400

    tokens = token_response.json()
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    # Use the access token to export email
    export_email(EMAIL_ID, access_token)

    return "Email details exported successfully!"


# Function to export email details using OAuth access token
def export_email(email_id, access_token):
    url = f'{BASE_API_URL}/marketing-emails/v1/emails/{email_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        logging.info(f"Successfully retrieved email details for ID {email_id}")
        email_data = response.json()

        # Save the email details to a JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(email_data, f, indent=4)
        logging.info(f"Email details saved to {OUTPUT_FILE}")
    else:
        logging.error(f"Failed to retrieve email details: {response.status_code} - {response.text}")


if __name__ == "__main__":
    app.run(debug=True)
