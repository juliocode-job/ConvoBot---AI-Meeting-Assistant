# database_setup.py
import chromadb

# Create a client. For development, this creates a temporary, 
# in-memory instance of ChromaDB.
client = chromadb.Client()

# Create a "collection." Think of this like a table in a traditional 
# database or a folder for a specific topic. We'll store all our 
# meeting memories here.
collection = client.create_collection(name="meeting_transcripts")

print("✅ ChromaDB client created successfully.")
print(f"✅ Collection '{collection.name}' created successfully.")
print("Database is ready to store memories!")