#!/usr/bin/env python3
"""
Example of correctly listing Qdrant collections.
Shows the proper way to access collection names from CollectionInfo objects.
"""

from qdrant_client import QdrantClient

# Initialize client
client = QdrantClient(url="http://localhost:6333")

# Get collections - returns CollectionsResponse with list of CollectionInfo objects
collections_response = client.get_collections()

# CORRECT way - CollectionInfo has 'name' attribute, not 'collection_name'
print("Collections in Qdrant:")
for collection_info in collections_response.collections:
    print(f"  - {collection_info.name}")  # ✓ CORRECT: use .name

# INCORRECT way that causes AttributeError
# for collection_info in collections_response.collections:
#     print(f"  - {collection_info.collection_name}")  # ✗ WRONG: no such attribute

# Alternative: Get list of collection names
collection_names = [c.name for c in collections_response.collections]
print(f"\nCollection names: {collection_names}")