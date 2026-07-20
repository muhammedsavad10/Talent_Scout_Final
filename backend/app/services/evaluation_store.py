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
        self._evaluations: Dict[str, Dict[str, Any]] = {}
        self._batches: Dict[str, Dict[str, Any]] = {}
        
    async def save_evaluation(self, evaluation_id: str, data: Dict[str, Any]) -> bool:
        self._evaluations[evaluation_id] = data
        logger.info(f"Saved evaluation {evaluation_id} to in-memory store.")
        return True
        
    async def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        return self._evaluations.get(evaluation_id)

    async def create_batch(self, batch_id: str, total: int) -> bool:
        self._batches[batch_id] = {
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
        logger.info(f"Created batch {batch_id} in memory.")
        return True

    async def update_batch_status(self, batch_id: str, status_data: Dict[str, Any]) -> bool:
        if batch_id in self._batches:
            self._batches[batch_id].update(status_data)
            return True
        return False
        
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        return self._batches.get(batch_id)

# Singleton instance
evaluation_store = EvaluationStore()
