import pandas as pd
import os
import re

# Load the data
file_path = '2024 befor sep 1 salesloft mip cadences.csv'
df = pd.read_csv(file_path)

# Function to clean up file names by removing special characters
def clean_file_name(name):
    return re.sub(r'[^\w\-]', '_', name)

# Group by the relevant columns
grouped_df = df.groupby(['Contact Owner', 'Most Recent Cadence - Last Step Number', 'Most Recent Cadence - Cadence Name'])

# Create an output folder if it doesn't exist
output_folder = "output_csv_files"
os.makedirs(output_folder, exist_ok=True)

# Save each group to a separate CSV file
for group_name, group_data in grouped_df:
    contact_owner = clean_file_name(group_name[0])
    last_step_number = group_name[1]
    cadence_name = clean_file_name(group_name[2])
    
    # Create a file name that reflects the group
    file_name = f"{contact_owner}_{last_step_number}_{cadence_name}.csv"
    
    # Save the group data to CSV
    group_data.to_csv(os.path.join(output_folder, file_name), index=False)

print(f"CSV files have been successfully saved to '{output_folder}'")
