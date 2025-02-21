import os
import json

# Get the current working directory
input_dir = os.getcwd()

# Directory to store the JSON files
output_dir = 'bibliography_json'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get all the .txt files in the current directory
files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]

# Dictionary to store the data for each person
person_data = {}

# Email mapping
email_mapping = {
    "andrei": "andrei.buciulea@urjc.es",
    "antonio": "antonio.garcia.marques@urjc.es",
    "victor": "victor.tenorio@urjc.es",
    "sergio": "sergio.rozada@urjc.es",
    "samuel": "samuel.rey.escudero@urjc.es",
    "fernando": "fernando.real.rojas@urjc.es"
}

# Process each .txt file
for file in files:
    # Check if the file is in Spanish or English
    if '_ES.txt' in file:
        name = file.replace('_ES.txt', '').lower()
        with open(os.path.join(input_dir, file), 'r', encoding='utf-8') as f:
            bibliography_es = f.read().splitlines()
        
        # Initialize the entry for this person if not already
        if name not in person_data:
            person_data[name] = {"bibliography_es": [], "bibliography_en": []}
        
        # Add the Spanish bibliography
        person_data[name]["bibliography_es"] = bibliography_es
        
    elif '_EN.txt' in file:
        name = file.replace('_EN.txt', '').lower()
        with open(os.path.join(input_dir, file), 'r', encoding='utf-8') as f:
            bibliography_en = f.read().splitlines()
        
        # Initialize the entry for this person if not already
        if name not in person_data:
            person_data[name] = {"bibliography_es": [], "bibliography_en": []}
        
        # Add the English bibliography
        person_data[name]["bibliography_en"] = bibliography_en
        
# Write the JSON files for each person
for name, data in person_data.items():
    # Create the JSON file path
    json_file_path = os.path.join(output_dir, f"{name}.json")
    
    # Add the name and email to the data and save as a JSON file
    json_data = {
        "name": name.capitalize(),
        "bibliography_es": data["bibliography_es"],
        "bibliography_en": data["bibliography_en"],
        "email": email_mapping.get(name, "unknown@urjc.es")  # Default email if not found
    }

    # Write the JSON data to the file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print(f"JSON files created in the folder '{output_dir}'.")


