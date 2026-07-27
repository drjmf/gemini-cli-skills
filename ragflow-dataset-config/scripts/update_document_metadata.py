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

def get_documents(api_key, dataset_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{API_BASE_URL}/datasets/{dataset_id}/documents", headers=headers)
    response.raise_for_status()
    data = response.json().get("data", {})
    return data if isinstance(data, list) else data.get("docs", [])

def update_document_metadata(api_key, dataset_id, document_id, metadata):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{API_BASE_URL}/datasets/{dataset_id}/documents/{document_id}"
    payload = {"meta_fields": metadata}
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single: python3 update_document_metadata.py --dataset \"DS Name\" --doc \"Doc Name\" --meta '{\"key\": \"val\"}'")
        print("  Bulk:   python3 update_document_metadata.py --file bulk_metadata.json")
        sys.exit(1)

    api_key = get_api_key()
    datasets_cache = {}

    def get_ds_id(name):
        if name in datasets_cache: return datasets_cache[name]
        datasets = get_datasets(api_key)
        for ds in datasets:
            if ds['name'] == name or ds['id'] == name:
                datasets_cache[name] = ds['id']
                return ds['id']
        return None

    if "--file" in sys.argv:
        file_path = sys.argv[sys.argv.index("--file") + 1]
        with open(file_path, 'r') as f:
            tasks = json.load(f)
        
        for task in tasks:
            ds_name = task.get('dataset')
            doc_name = task.get('document')
            meta = task.get('metadata')
            
            ds_id = get_ds_id(ds_name)
            if not ds_id:
                print(f"Error: Dataset '{ds_name}' not found.")
                continue
            
            docs = get_documents(api_key, ds_id)
            doc_id = next((d['id'] for d in docs if d['name'] == doc_name or d['id'] == doc_name), None)
            
            if not doc_id:
                print(f"Error: Document '{doc_name}' not found in dataset '{ds_name}'.")
                continue
            
            res = update_document_metadata(api_key, ds_id, doc_id, meta)
            print(f"Updated '{doc_name}': {res.get('message', 'Success')}")

    elif "--dataset" in sys.argv and "--doc" in sys.argv and "--meta" in sys.argv:
        ds_name = sys.argv[sys.argv.index("--dataset") + 1]
        doc_name = sys.argv[sys.argv.index("--doc") + 1]
        meta = json.loads(sys.argv[sys.argv.index("--meta") + 1])
        
        ds_id = get_ds_id(ds_name)
        if not ds_id:
            print(f"Error: Dataset '{ds_name}' not found.")
            sys.exit(1)
            
        docs = get_documents(api_key, ds_id)
        doc_id = next((d['id'] for d in docs if d['name'] == doc_name or d['id'] == doc_name), None)
        
        if not doc_id:
            print(f"Error: Document '{doc_name}' not found in dataset '{ds_name}'.")
            sys.exit(1)
            
        res = update_document_metadata(api_key, ds_id, doc_id, meta)
        print(f"Result: {res.get('code')} - {res.get('message', 'Success')}")

if __name__ == "__main__":
    main()
