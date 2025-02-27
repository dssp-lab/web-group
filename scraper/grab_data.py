import os
import json

from scraper.mail_utils import send_email

def create_empty_json_files():
    folder_name = "jsons"
    file_names = ["projects.json", "papers.json"]
    
    # Create folder if it does not exist
    os.makedirs(folder_name, exist_ok=True)
    
    # Create empty JSON files
    for file_name in file_names:
        file_path = os.path.join(folder_name, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump({}, file)  # Writing an empty JSON object
            print(f"Created: {file_path}")
        else:
            print(f"Already exists: {file_path}")

if __name__ == "__main__":
    create_empty_json_files()
    send_email("victor.030995@gmail.com", "Test email", "Test email")