import os
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

PIXELDRAIN_UPLOAD_URL = os.getenv("PIXELDRAIN_UPLOAD_URL")
PIXELDRAIN_VIEW_URL = os.getenv("PIXELDRAIN_VIEW_URL")
VISIT_INTERVAL = int(os.getenv("VISIT_INTERVAL", 120)) 
JSON_FILE = os.getenv("JSON_FILE")
API_KEY = os.getenv("API_KEY")

def get_auth():
    return requests.auth.HTTPBasicAuth('', API_KEY)

def upload_file(file_path):
    """Upload a file to Pixeldrain and return the file ID and timestamp."""
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(PIXELDRAIN_UPLOAD_URL, files={"file": file}, auth=get_auth())
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content.decode('utf-8')}")

        if response.status_code in [200, 201]:
            file_id = response.json().get('id')
            timestamp = response.headers.get('Date')
            timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z').isoformat()
            return file_id, timestamp
        else:
            raise Exception(f"Upload failed with status code {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise

def update_json_file(file_id, timestamp):
    """Add or update the file ID in the JSON file."""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"JSON file {JSON_FILE} is empty or corrupted. Initializing new JSON data.")
                    data = {}
        else:
            data = {}
        
        data[file_id] = timestamp
        
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Updated JSON file: {JSON_FILE}")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Exception occurred while updating JSON file: {str(e)}")
        raise

def keepalive():
    """Visit all files in the JSON file that haven't been visited in the last VISIT_INTERVAL days."""
    if not os.path.exists(JSON_FILE):
        print(f"No {JSON_FILE} found. Please upload a file first.")
        return

    with open(JSON_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"JSON file {JSON_FILE} is empty or corrupted.")
            return

    current_time = datetime.now()
    updated = False

    for file_id, last_visited in data.items():
        try:
            last_visit_time = datetime.fromisoformat(last_visited)
        except ValueError:
            # Handle non-ISO format by converting it
            last_visit_time = datetime.strptime(last_visited, '%a, %d %b %Y %H:%M:%S %Z')
        
        if current_time - last_visit_time >= timedelta(days=VISIT_INTERVAL):
            url = f"{PIXELDRAIN_VIEW_URL}/{file_id}/info"
            try:
                response = requests.get(url, auth=get_auth())
                if response.status_code == 200:
                    data[file_id] = current_time.isoformat()
                    print(f"Successfully visited {url}")
                    updated = True
                else:
                    print(f"Failed to visit {url}. Status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error visiting {url}: {str(e)}")
        else:
            print(f"Skipped {file_id} (Last visit: {last_visited})")

    if updated:
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated JSON file after keepalive: {JSON_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Pixeldrain file uploader and keepalive script")
    parser.add_argument("--upload", help="Upload a file to Pixeldrain")
    parser.add_argument("--alive", action="store_true", help="Keep files alive by visiting them")
    args = parser.parse_args()

    if args.upload:
        try:
            file_id, timestamp = upload_file(args.upload)
            update_json_file(file_id, timestamp)
            print(f"File uploaded successfully. File ID: {file_id}")
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
    elif args.alive:
        keepalive()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()