import json
import os
import sys

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

def check_drift():
    saved_schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openapi.json")
    if not os.path.exists(saved_schema_path):
        print(f"[-] No saved schema found at: {saved_schema_path}")
        sys.exit(1)
        
    with open(saved_schema_path, "r", encoding="utf-8") as f:
        saved_schema = json.load(f)
        
    current_schema = app.openapi()
    
    # Simple check by comparing serialized content
    saved_str = json.dumps(saved_schema, sort_keys=True)
    current_str = json.dumps(current_schema, sort_keys=True)
    
    if saved_str != current_str:
        print("[!] API CONTRACT DRIFT DETECTED!")
        print("    The FastAPI app schemas have changed, but openapi.json was not updated.")
        print("    Please run: python scripts/export_openapi.py and regenerate types.")
        sys.exit(1)
    else:
        print("[+] API Contract matches saved schema. No drift detected.")
        sys.exit(0)

if __name__ == "__main__":
    check_drift()
