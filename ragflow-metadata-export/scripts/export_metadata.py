import json, requests, os, sys, argparse

SECRETS_FILE = "/opt/mycelia-ai-stack/.secrets"
API_BASE_URL = "http://127.0.0.1:8081/api/v1"

def get_api_key():
    if not os.path.exists(SECRETS_FILE):
        return None
    with open(SECRETS_FILE, "r") as f:
        for line in f:
            if line.startswith("RAGFLOW_API_KEY="):
                return line.split("=")[1].strip().strip('"')
    return None

def main():
    parser = argparse.ArgumentParser(description="Export RagFlow document names and metadata to JSON")
    parser.add_argument("--prefix", help="Only export datasets starting with this prefix (e.g., 'en')", default="")
    parser.add_argument("--output", help="Path to save the JSON file", default="/opt/mycelia-ai-stack/scripts/ragflow_metadata_export.json")
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("API Key not found")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}

    # 1. Get all datasets
    res = requests.get(f"{API_BASE_URL}/datasets?page=1&page_size=100", headers=headers)
    datasets = res.json().get("data", [])

    export_data = []

    for ds in datasets:
        ds_name = ds['name']
        if ds_name.lower().startswith(args.prefix.lower()):
            print(f"Processing Dataset: {ds_name} (ID: {ds['id']})")
            
            ds_id = ds['id']
            # List all documents and their metadata with pagination
            page = 1
            page_size = 100
            while True:
                doc_res = requests.get(f"{API_BASE_URL}/datasets/{ds_id}/documents?page={page}&page_size={page_size}", headers=headers)
                res_json = doc_res.json()
                data = res_json.get("data")
                if not data:
                    print(f"  - No documents found or error for '{ds_name}' at page {page}")
                    break
                    
                docs = data.get("docs", []) if isinstance(data, dict) else []
                if not docs:
                    break

                for doc in docs:
                    export_data.append({
                        "dataset_name": ds_name,
                        "dataset_id": ds_id,
                        "document_name": doc['name'],
                        "document_id": doc['id'],
                        "metadata": doc.get("meta_fields", {})
                    })
                
                if len(docs) < page_size:
                    break
                page += 1

    # Write to JSON file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(args.output, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"\nExport complete! File created at: {args.output}")
    print(f"Total documents exported: {len(export_data)}")

if __name__ == "__main__":
    main()
