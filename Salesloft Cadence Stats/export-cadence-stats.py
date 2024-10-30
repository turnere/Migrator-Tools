import requests
import pandas as pd
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO)

# Define the API instances and the corresponding cadence IDs
# Each key in this dictionary is an API key, and the values are lists of cadence IDs for that key
cadence_instances = {
    os.getenv('SLGS_API_KEY'): ["1485723"],  # Add your actual cadence IDs
    os.getenv('SLMIP_API_KEY'): ["1472475", "1486651"],  # Replace with real cadence IDs
}

# Prepare an empty list to store all the cadence data
all_cadence_data = []

# Iterate through each API key and the associated cadence IDs
for api_key, cadence_ids in cadence_instances.items():
    
    # Headers with the authentication token
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    for cadence_id in cadence_ids:
        url = f"https://api.salesloft.com/v2/cadence_stats/{cadence_id}"

        # Make the API request
        logging.info(f"Fetching cadence stats for cadence ID: {cadence_id}")
        response = requests.get(url, headers=headers)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract relevant details, including the cadence name
            # Adjust based on the actual JSON response structure
            if 'data' in data:
                cadence_stats = data['data']
                cadence_name = cadence_stats.get('name', 'Unknown Cadence Name')
                
                # Add the cadence ID and name to the stats data
                cadence_stats['cadence_id'] = cadence_id
                cadence_stats['cadence_name'] = cadence_name
                
                # Append the cadence stats to the list
                all_cadence_data.append(cadence_stats)
            
            logging.info(f"Data retrieved successfully for cadence ID {cadence_id}.")
        else:
            logging.error(f"Failed to retrieve data for cadence ID {cadence_id}. Status Code: {response.status_code}, Response: {response.text}")

# Convert the list of cadence data to a DataFrame
df = pd.DataFrame(all_cadence_data)

# Export the data to Excel
output_file = 'cadence_stats_multiple_instances.xlsx'
df.to_excel(output_file, index=False)

logging.info(f"Data exported to {output_file}")
