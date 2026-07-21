import json
from app.models.schemas import DimensionMetadata

def _serialize(obj):
    print("Called serialize on", type(obj))
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    return str(obj)

meta = DimensionMetadata(score=100, confidence=100, weight=0.5, evidence=[])
data = {"test": meta}
try:
    print(json.dumps(data, default=_serialize))
except Exception as e:
    print("Error:", e)
