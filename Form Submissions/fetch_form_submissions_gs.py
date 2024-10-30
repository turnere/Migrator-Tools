import requests
import pandas as pd
from urllib.parse import urljoin
import logging
import re  # Import regex library for extracting form ID
from dotenv import load_dotenv
import os

# Constants
load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv('GS_API_KEY')  # Replace with your actual API key
BASE_API_URL = 'https://api.hubapi.com/form-integrations/v1/submissions/forms/'  # Base URL for HubSpot form submissions API
LIMIT50 = '?limit=50'

# Configure logging
logging.basicConfig(
    filename='fetch_form_submissions.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_base_url(url):
    return url.split('?')[0] if url else None  # Check if URL is not None

# Function to extract the form ID from the form URL
def extract_form_id(form_url):
    match = re.search(r'/forms/([^?]+)', form_url)
    return match.group(1) if match else None

def fetch_submissions(url, form_url):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    base_urls = []  # List to store base URLs for the current form
    
    while url:
        logging.debug(f"Fetching URL: {url}")  # Log URL being fetched
        
        response = requests.get(url, headers=headers)
        
        # Check for HTTP errors
        if response.status_code != 200:
            logging.error(f"Error fetching data: {response.status_code} - {response.text}")
            break
        
        try:
            data = response.json()  # Attempt to parse JSON
        except requests.exceptions.JSONDecodeError:
            logging.error(f"Failed to parse JSON response from {url}. Response text: {response.text}")
            break
        
        if 'results' in data:
            logging.debug(f"Number of results on this page: {len(data['results'])}")  # Log number of results
            
            for submission in data['results']:
                page_url = submission.get('pageUrl')  # Safely get 'pageUrl'
                if page_url:  # Only process if 'pageUrl' is not None
                    base_url = get_base_url(page_url)
                    if base_url:
                        if base_url not in base_urls:
                            logging.info(f"New base URL found: {base_url}")  # Log new base URLs
                            base_urls.append(base_url)  # Add base URL to the list
        
        # Handle pagination
        if 'paging' in data and 'next' in data['paging']:
            next_link = data['paging']['next']['link']
            # Ensure the next link is correctly appended to the form URL
            if next_link.startswith('/'):
                url = urljoin(form_url, next_link, LIMIT50)
            else:
                url = urljoin(form_url, next_link, LIMIT50)
            logging.debug(f"Next page URL: {url}")  # Log next page URL
        else:
            url = None
    
    return base_urls

def main():
    # Load form IDs from CSV file
    df_form_ids = pd.read_csv('form_ids.csv')  # Assuming CSV has a column "Form ID"
    form_ids = df_form_ids['Form ID'].tolist()  # Extract form IDs from CSV
    
    all_results = []  # List to store results
    
    for form_id in form_ids:
        form_url = f"{BASE_API_URL}{form_id}{LIMIT50}"  # Construct the full form URL
        logging.info(f"Processing form ID: {form_id}, URL: {form_url}")  # Log the form ID and URL being processed
        
        submission_urls = fetch_submissions(form_url, form_url)
        
        if submission_urls:
            for base_url in submission_urls:
                all_results.append((form_url, base_url, form_id))  # Add form ID to results
        else:
            logging.info(f"No submission URLs found for form ID: {form_id}")  # Log if no URLs are found
    
    # Convert the list to a DataFrame with 'Form URL', 'Base URL', and 'Form ID' columns
    df = pd.DataFrame(all_results, columns=['Form URL', 'Base URL', 'Form ID'])
    df.to_csv('form_base_urls_with_ids.csv', index=False)
    logging.info("Data saved to form_base_urls_with_ids.csv")

if __name__ == "__main__":
    main()