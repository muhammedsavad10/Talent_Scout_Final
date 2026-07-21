import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db.clients import supabase_db

def test():
    try:
        res = supabase_db.table("batches").select("*").limit(1).execute()
        print("batches table exists:", res.data)
    except Exception as e:
        print("Error reading batches:", e)

if __name__ == "__main__":
    test()
