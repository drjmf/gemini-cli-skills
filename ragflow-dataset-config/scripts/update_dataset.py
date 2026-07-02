import json
import requests
import sys
import os

# Configuration
API_BASE_URL = "http://127.0.0.1:8081/api/v1"
SECRETS_FILE = "/opt/mycelia-ai-stack/.secrets"

def get_api_key():
    if not os.path.exists(SECRETS_FILE):
        print(f"Error: Secrets file {SECRETS_FILE} not found.")
        sys.exit(1)
    with open(SECRETS_FILE, 'r') as f:
        for line in f:
            if line.startswith("RAGFLOW_API_KEY="):
                return line.split("=")[1].strip().strip('"')
    print("Error: RAGFLOW_API_KEY not found in secrets file.")
    sys.exit(1)

def get_datasets(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{API_BASE_URL}/datasets", headers=headers)
    response.raise_for_status()
    return response.json().get("data", [])

def update_dataset_general(api_key, dataset_id, payload):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{API_BASE_URL}/datasets/{dataset_id}"
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

def update_dataset_metadata(api_key, dataset_id, metadata_fields):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{API_BASE_URL}/datasets/{dataset_id}/metadata/config"
    payload = {
        "metadata": metadata_fields,
        "built_in_metadata": [] # Usually kept empty or default
    }
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 update_dataset.py <dataset_name_or_id> <config_json_path>")
        sys.exit(1)

    target = sys.argv[1]
    config_path = sys.argv[2]
    api_key = get_api_key()

    with open(config_path, 'r') as f:
        config = json.load(f)

    datasets = get_datasets(api_key)
    dataset_id = None
    
    for ds in datasets:
        if ds['id'] == target or ds['name'] == target:
            dataset_id = ds['id']
            break

    if not dataset_id:
        print(f"Error: Dataset '{target}' not found.")
        sys.exit(1)

    print(f"Updating dataset '{target}' (ID: {dataset_id})...")
    
    # 1. Update General Settings (Language, etc.)
    if "dataset_settings" in config:
        print("Updating general settings (language)...")
        gen_payload = {}
        if "language" in config["dataset_settings"]:
            gen_payload["language"] = config["dataset_settings"]["language"]
        if "description" in config["dataset_settings"]:
            gen_payload["description"] = config["dataset_settings"]["description"]
        
        res = update_dataset_general(api_key, dataset_id, gen_payload)
        print(f"General update result: {res.get('code')} - {res.get('message', 'Success')}")

    # 2. Update Metadata Generation Settings
    if "metadata_generation_settings" in config:
        print("Updating metadata generation settings...")
        metadata_fields = []
        for field in config["metadata_generation_settings"]:
            # Type mapping: RagFlow UI uses 'list' but API validation says Literal["string", "list", "time", "number"]
            # So the mapping is direct.
            metadata_fields.append({
                "key": field["key"],
                "type": field["type"],
                "description": field.get("description", ""),
                "enum": field.get("enum", [])
            })
            
        res = update_dataset_metadata(api_key, dataset_id, metadata_fields)
        print(f"Metadata update result: {res.get('code')} - {res.get('message', 'Success')}")

if __name__ == "__main__":
    main()
