"""
Reconstructed Evaluation Store for Phase C4B.
Uses an in-memory dictionary fallback to ensure end-to-end flow works
without requiring a live Supabase connection during reconstruction testing.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EvaluationStore:
    def __init__(self):
        from app.db.clients import supabase_db
        self.db = supabase_db
        self._batches: Dict[str, Dict[str, Any]] = {} # Fallback for batches if no table exists

    async def save_evaluation(self, evaluation_id: str, data: Dict[str, Any]) -> bool:
        import json
        def _serialize(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            elif hasattr(obj, "dict"):
                return obj.dict()
            return str(obj)
            
        try:
            serialized_data = json.loads(json.dumps(data, default=_serialize))
            self.db.table("evaluations").upsert({
                "id": evaluation_id,
                "data": serialized_data
            }).execute()
            logger.info(f"Saved evaluation {evaluation_id} to Supabase.")
            return True
        except Exception as e:
            logger.error(f"Failed to save evaluation {evaluation_id}: {e}")
            return False
        
    async def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.db.table("evaluations").select("data").eq("id", evaluation_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0].get("data")
            return None
        except Exception as e:
            logger.error(f"Failed to get evaluation {evaluation_id}: {e}")
            return None

    async def create_batch(self, batch_id: str, total: int) -> bool:
        # Save batch state to evaluations table using the batch_id as the primary key
        batch_data = {
            "batch_id": batch_id,
            "status": "PROCESSING",
            "total": total,
            "completed": 0,
            "processing": total,
            "queued": 0,
            "failed": 0,
            "successfully_evaluated": 0,
            "results": {"ranked_candidates": []},
            "raw_evaluations": []
        }
        return await self.save_evaluation(batch_id, batch_data)

    async def update_batch_status(self, batch_id: str, status_data: Dict[str, Any]) -> bool:
        current_data = await self.get_evaluation(batch_id)
        if current_data:
            current_data.update(status_data)
            return await self.save_evaluation(batch_id, current_data)
        return False
        
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        return await self.get_evaluation(batch_id)

# Singleton instance
evaluation_store = EvaluationStore()
