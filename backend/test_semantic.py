import sys
import os
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.agents.scout import initialize_qdrant_collection, get_embedding, index_resume, semantic_search

def test():
    print("Initializing Qdrant...")
    initialize_qdrant_collection()
    
    print("Generating embedding for sample text...")
    emb = get_embedding("I am a Python developer")
    assert len(emb) == 384
    print("Embedding generation successful.")
    
    print("Indexing mock resume...")
    eval_id = "test-eval-1234"
    index_resume(eval_id, "Highly experienced Python developer with 10 years of experience.", {"candidate_name": "Alice"})
    
    # Allow some time for indexing
    time.sleep(1)
    
    print("Performing semantic search...")
    results = semantic_search("Looking for Python expertise")
    
    print(f"Found {len(results)} results:")
    for res in results:
        print(res)
    
    assert len(results) > 0
    print("Semantic search successful.")

if __name__ == "__main__":
    test()
