"""
Shared pytest configuration and global mocks.
Ensures no real network calls are made to Supabase or Qdrant when modules are imported.
"""
import os
from unittest.mock import MagicMock
import supabase
import qdrant_client

# Mock required environment variables before app settings are imported
os.environ["SUPABASE_URL"] = "http://mock-supabase.local"
os.environ["SUPABASE_KEY"] = "mock-key"
os.environ["QDRANT_URL"] = "http://mock-qdrant.local"
os.environ["QDRANT_API_KEY"] = "mock-qdrant-key"

# Mock the client constructors globally at import time to prevent real network requests/checks
mock_supabase_client = MagicMock()
mock_qdrant_client = MagicMock()

# Mocking supabase.create_client
supabase.create_client = MagicMock(return_value=mock_supabase_client)

# Mocking qdrant_client.QdrantClient
# This prevents the constructor from calling home/version-checking.
qdrant_client.QdrantClient = MagicMock(return_value=mock_qdrant_client)

# Mocking sentence_transformers.SentenceTransformer globally at import time
import sentence_transformers
import numpy as np

mock_transformer_instance = MagicMock()
mock_transformer_instance.encode.return_value = np.zeros(384)

sentence_transformers.SentenceTransformer = MagicMock(return_value=mock_transformer_instance)

