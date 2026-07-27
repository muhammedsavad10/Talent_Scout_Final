"""
TalentScout Enterprise Version 1.0 — Phase D Database & Persistence Test Suite.
Validates database connection resilience, memory fallback modes, TTL cache expiration, and batch store persistence.
"""
import asyncio
import pytest
from app.db.clients import is_supabase_healthy, is_qdrant_healthy, get_supabase_client, get_qdrant_client
from app.services.evaluation_store import evaluation_store
from app.services.cache_service import CacheService

@pytest.mark.asyncio
async def test_phase_d_db_fallback_resilience():
    """Verify database clients handle missing credentials gracefully without crashing."""
    supabase = get_supabase_client(retries=1, raise_on_error=False)
    qdrant = get_qdrant_client(retries=1, raise_on_error=False)
    # Functions should return None or client object cleanly without unhandled exception
    assert supabase is None or hasattr(supabase, "table")
    assert qdrant is None or hasattr(qdrant, "get_collections")

@pytest.mark.asyncio
async def test_phase_d_evaluation_store_fallback():
    """Verify EvaluationStore saves and retrieves evaluations via memory fallback."""
    eval_id = "test_eval_phase_d_001"
    eval_data = {"result": {"hiring_priority_score": 88.5, "candidate_facts": {"name": "Test Candidate"}}}
    
    saved = await evaluation_store.save_evaluation(eval_id, eval_data)
    assert saved is True
    
    retrieved = await evaluation_store.get_evaluation(eval_id)
    assert retrieved is not None
    assert retrieved.get("result", {}).get("hiring_priority_score") == 88.5

@pytest.mark.asyncio
async def test_phase_d_cache_ttl_expiration():
    """Verify CacheService expires entries when TTL is exceeded."""
    cache = CacheService(max_items=10)
    await cache.set("short_key", "short_val", ttl=1)
    
    val_before = await cache.get("short_key")
    assert val_before == "short_val"
    
    # Wait for TTL expiration
    await asyncio.sleep(1.1)
    val_after = await cache.get("short_key")
    assert val_after is None

@pytest.mark.asyncio
async def test_phase_d_cache_capacity_eviction():
    """Verify CacheService evicts oldest item when max capacity is reached."""
    cache = CacheService(max_items=2)
    await cache.set("k1", "v1")
    await cache.set("k2", "v2")
    await cache.set("k3", "v3") # Triggers eviction of k1
    
    assert await cache.get("k1") is None
    assert await cache.get("k2") == "v2"
    assert await cache.get("k3") == "v3"

@pytest.mark.asyncio
async def test_phase_d_concurrent_cache_access():
    """Verify concurrent reads and writes to CacheService operate safely without race conditions."""
    cache = CacheService(max_items=100)
    
    async def writer(i: int):
        await cache.set(f"concurrent_k_{i}", f"val_{i}")
        
    tasks = [writer(i) for i in range(20)]
    await asyncio.gather(*tasks)
    
    val_10 = await cache.get("concurrent_k_10")
    assert val_10 == "val_10"
