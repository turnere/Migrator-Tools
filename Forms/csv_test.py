import logging

# Configure logging
logging.basicConfig(
    filename='create_forms.log',
    level=logging.DEBUG,  # Set to DEBUG level to capture all messages
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Function to load CSV and create a mapping of external name to internal name

# Function to load CSV and create a mapping of external name to internal name
# Use print statements if logging isn't necessary
def load_field_mappings(csv_file):
    field_mappings = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Print the headers of the CSV
        print(f"CSV Headers: {reader.fieldnames}")  # Debug print statement
        
        for row in reader:
            print(f"Row: {row}")  # Print the current row for debugging
            
            # Check if 'external_name' and 'gs_internal_name' exist in the row
            external_name = row.get('external_name', '').strip()
            internal_name = row.get('gs_internal_name', '').strip()
            
            if external_name and internal_name:
                field_mappings[external_name] = internal_name
            else:
                print(f"Skipping row with missing values: {row}")  # Print skipped rows for debugging
                
    return field_mappings

