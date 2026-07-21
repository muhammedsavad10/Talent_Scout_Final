import os
import sys
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db.clients import supabase_db

def test():
    try:
        # Fetch the specific batch
        res = supabase_db.table("evaluations").select("*").eq("id", "e1584403-592c-42d7-8840-3692093631b7").execute()
        if res.data:
            print(json.dumps(res.data[0], indent=2))
        else:
            print("Batch not found in db.")
    except Exception as e:
        print("Error reading:", e)

if __name__ == "__main__":
    test()
