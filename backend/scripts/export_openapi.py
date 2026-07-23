import json
import os
import sys

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

def export_schema():
    schema = app.openapi()
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openapi.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"[+] Successfully exported OpenAPI schema to: {output_path}")

if __name__ == "__main__":
    export_schema()
