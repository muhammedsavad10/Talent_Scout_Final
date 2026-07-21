import os
import sys
import time
import uuid

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings, call_llm
from app.db.clients import supabase_db, qdrant_db
from sentence_transformers import SentenceTransformer

def check_supabase():
    start = time.time()
    try:
        test_data = {
            "filename": "test_verify_live_deps.pdf",
            "raw_resume_text": "text",
            "parsed_data_json": {"test": True}
        }
        # Insert
        res = supabase_db.table("candidates").insert(test_data).execute()
        test_id = res.data[0]["id"] if res.data and "id" in res.data[0] else None
        
        if test_id:
            # Read
            read_res = supabase_db.table("candidates").select("*").eq("id", test_id).execute()
            assert len(read_res.data) > 0, "Row not found after insert"
            # Delete
            supabase_db.table("candidates").delete().eq("id", test_id).execute()
        
        latency = (time.time() - start) * 1000
        return "Pass", latency
    except Exception as e:
        return f"Fail: {e}", (time.time() - start) * 1000

def check_qdrant():
    start = time.time()
    try:
        from qdrant_client.models import PointStruct, VectorParams, Distance
        
        test_id = str(uuid.uuid4())
        collection_name = "test_verify_collection"
        
        # Ensure collection exists
        if not qdrant_db.collection_exists(collection_name):
             qdrant_db.create_collection(
                 collection_name=collection_name,
                 vectors_config=VectorParams(size=384, distance=Distance.COSINE)
             )
        
        vector = [0.1] * 384
        # Upsert
        qdrant_db.upsert(
            collection_name=collection_name,
            points=[PointStruct(id=test_id, vector=vector, payload={"test": True})]
        )
        
        # Retrieve
        res = qdrant_db.retrieve(
            collection_name=collection_name,
            ids=[test_id]
        )
        assert len(res) > 0, "Vector not found after upsert"
        
        # Delete point
        qdrant_db.delete(
            collection_name=collection_name,
            points_selector=[test_id]
        )
        
        latency = (time.time() - start) * 1000
        return "Pass", latency
    except Exception as e:
        return f"Fail: {e}", (time.time() - start) * 1000

def check_sentence_transformer():
    start = time.time()
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = model.encode("This is a test document.")
        assert len(emb) == 384
        latency = (time.time() - start) * 1000
        return "Pass", latency
    except Exception as e:
        return f"Fail: {e}", (time.time() - start) * 1000

def check_groq():
    start = time.time()
    try:
        messages = [{"role": "user", "content": "Extract the name from this text: My name is John Doe. Return only the name."}]
        res = call_llm(messages, max_tokens=10)
        assert "John" in res, f"Expected 'John' in response, got '{res}'"
        
        latency = (time.time() - start) * 1000
        return "Pass", latency
    except Exception as e:
        return f"Fail: {e}", (time.time() - start) * 1000

if __name__ == "__main__":
    print(f"{'Dependency':<20} | {'Check':<40} | {'Result':<10} | {'Latency (ms)':<10}")
    print("-" * 85)
    
    res, lat = check_groq()
    print(f"{'Groq':<20} | {'Parse sample resume':<40} | {res:<10} | {lat:.2f}")
    
    res, lat = check_sentence_transformer()
    print(f"{'SentenceTransformer':<20} | {'Generate embedding':<40} | {res:<10} | {lat:.2f}")
    
    res, lat = check_qdrant()
    print(f"{'Qdrant':<20} | {'Upsert + Retrieve + Delete test vector':<40} | {res:<10} | {lat:.2f}")
    
    res, lat = check_supabase()
    print(f"{'Supabase':<20} | {'Insert + Read + Delete test row':<40} | {res:<10} | {lat:.2f}")
