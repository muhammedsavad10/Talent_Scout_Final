"""
Shared pytest configuration and global mocks.
Ensures no real network calls are made to Supabase or Qdrant when modules are imported.
"""
from unittest.mock import MagicMock
import supabase
import qdrant_client

# Mock the client constructors globally at import time to prevent real network requests/checks
mock_supabase_client = MagicMock()
mock_qdrant_client = MagicMock()

# Mocking supabase.create_client
supabase.create_client = MagicMock(return_value=mock_supabase_client)

# Mocking qdrant_client.QdrantClient
# This prevents the constructor from calling home/version-checking.
qdrant_client.QdrantClient = MagicMock(return_value=mock_qdrant_client)
