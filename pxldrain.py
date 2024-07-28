import os
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print

load_dotenv()

console = Console()

PIXELDRAIN_UPLOAD_URL = os.getenv("PIXELDRAIN_UPLOAD_URL")
PIXELDRAIN_VIEW_URL = os.getenv("PIXELDRAIN_VIEW_URL")
VISIT_INTERVAL = int(os.getenv("VISIT_INTERVAL", 120)) 
JSON_FILE = os.getenv("JSON_FILE")
API_KEY = os.getenv("API_KEY")

def get_auth():
    return requests.auth.HTTPBasicAuth('', API_KEY)

def upload_file(file_path):
    """Upload a file to Pixeldrain and return the file ID, timestamp, and file link."""
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(PIXELDRAIN_UPLOAD_URL, files={"file": file}, auth=get_auth())
        
        if response.status_code in [200, 201]:
            file_id = response.json().get('id')
            timestamp = response.headers.get('Date')
            timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z').isoformat()
            file_link = f"{PIXELDRAIN_VIEW_URL}/{file_id}"
            return file_id, timestamp, file_link
        else:
            raise Exception(f"Upload failed with status code {response.status_code}")
    except Exception as e:
        console.print(f"[bold red]Exception occurred:[/bold red] {str(e)}")
        raise

def update_json_file(file_id, timestamp):
    """Add or update the file ID in the JSON file."""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    console.print(f"[bold yellow]JSON file {JSON_FILE} is empty or corrupted. Initializing new JSON data.[/bold yellow]")
                    data = {}
        else:
            data = {}
        timestamp = datetime.fromisoformat(timestamp).isoformat()
        data[file_id] = timestamp
        
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"[bold green]Updated JSON file:[/bold green] [grey]{JSON_FILE}[/grey]")
    except Exception as e:
        console.print(f"[bold red]Exception occurred while updating JSON file:[/bold red] {str(e)}")
        raise

def keepalive():
    """Visit all files in the JSON file that haven't been visited in the last VISIT_INTERVAL days."""
    if not os.path.exists(JSON_FILE):
        console.print(f"[bold red]No {JSON_FILE} found. Please upload a file first.[/bold red]")
        return

    with open(JSON_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            console.print(f"[bold red]JSON file {JSON_FILE} is empty or corrupted.[/bold red]")
            return

    current_time = datetime.now()
    updated = False

    for file_id, last_visited in data.items():
        try:
            last_visit_time = datetime.fromisoformat(last_visited)
        except ValueError:
            last_visit_time = datetime.strptime(last_visited, '%a, %d %b %Y %H:%M:%S %Z')
        
        if current_time - last_visit_time >= timedelta(days=VISIT_INTERVAL):
            url = f"{PIXELDRAIN_VIEW_URL}/{file_id}"
            try:
                response = requests.get(url, auth=get_auth())
                if response.status_code == 200:
                    data[file_id] = current_time.isoformat()
                    console.print(f"[bold green]Successfully visited {url}[/bold green]")
                    updated = True
                else:
                    console.print(f"[bold red]Failed to visit {url}. Status code: {response.status_code}[/bold red]")
            except requests.RequestException as e:
                console.print(f"[bold red]Error visiting {url}:[/bold red] {str(e)}")
        else:
            console.print(f"[bold yellow]Skipped [bold green]{file_id}[/bold green] (Last visit: [bold yellow]{last_visited}[/bold yellow])[/bold yellow]")

    if updated:
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        console.print(f"[bold green]Updated JSON file after keepalive:[/bold green] [grey]{JSON_FILE}[/grey]")

def main():
    parser = argparse.ArgumentParser(description="Pixeldrain file uploader and keepalive script")
    parser.add_argument("--upload", help="Upload a file to Pixeldrain. Provide the file path as the argument.")
    parser.add_argument("--alive", action="store_true", help="Keep files alive by visiting them periodically.")
    args = parser.parse_args()

    if args.upload:
        try:
            file_id, timestamp, file_link = upload_file(args.upload)
            update_json_file(file_id, timestamp)
            console.print(f"[bold green]File uploaded successfully. File ID: {file_id}[/bold green]")
            console.print(f"[bold green]File link:[/bold green] [bold blue]{file_link}[/bold blue]")
        except Exception as e:
            console.print(f"[bold red]Error uploading file:[/bold red] {str(e)}")
    elif args.alive:
        keepalive()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()