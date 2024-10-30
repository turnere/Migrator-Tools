import csv
import json

# Assuming the JSON data is saved in a file named 'properties.json'
with open('specific_contact_properties.json', 'r') as json_file:
    properties_data = json.load(json_file)

# Open a CSV file to write the data
with open('properties_for_creation.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write the header
    writer.writerow([
        'Name', 'Label', 'Type', 'Field Type', 'Group Name', 'Option Label', 'Option Value',
        'Option Description', 'Option Display Order', 'Option Hidden'
    ])

    # Iterate over each property in the JSON data
    for property in properties_data:
        name = property.get('name', '')
        label = property.get('label', '')
        property_type = property.get('type', '')
        field_type = property.get('fieldType', '')
        group_name = property.get('groupName', '')

        # If the property has options, we need to iterate over them
        if 'options' in property:
            for option in property['options']:
                option_label = option.get('label', '')
                option_value = option.get('value', '')
                option_description = option.get('description', '')
                option_display_order = option.get('displayOrder', '')
                option_hidden = option.get('hidden', '')

                # Write the property and its options to the CSV file
                writer.writerow([
                    name, label, property_type, field_type, group_name,
                    option_label, option_value, option_description,
                    option_display_order, option_hidden
                ])
        else:
            # If no options, still write the property with empty option fields
            writer.writerow([name, label, property_type, field_type, group_name, '', '', '', '', ''])

print("Properties data has been saved to properties_for_creation.csv")

