# ingest_memory.py (Final Corrected Version)
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# --- Configuration ---
# This ensures the database is saved in your project folder
DB_PATH = "./chroma_db" 
COLLECTION_NAME = "meeting_transcripts"
TRANSCRIPT_FILE = "project_phoenix_transcript.txt" # Your transcript file

# --- Main Ingestion Logic ---
print("Starting persistent memory ingestion...")

# 1. Load environment variables (for the OPENAI_API_KEY)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("[FATAL ERROR] OPENAI_API_KEY not found in .env file.")
    print("Please make sure your .env file is set up correctly.")
else:
    try:
        # 2. Define the embedding function using OpenAI
        # This forces it to use the same model as your main.py
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small"
        )

        # 3. Initialize a PERSISTENT client
        client = chromadb.PersistentClient(path=DB_PATH)

        # 4. Get or create the collection with the correct embedding function
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=openai_ef
        )

        # 5. Read and chunk the transcript
        with open(TRANSCRIPT_FILE, 'r') as f:
            transcript = f.read()
        
        # Simple chunking
        chunks = [transcript[i:i+500] for i in range(0, len(transcript), 500)]
        print(f"Transcript split into {len(chunks)} chunks.")

        # 6. Add chunks to the database
        ids = [f"chunk_{i+1}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)

        print("\nPersistent memory ingestion complete!")
        print(f"Added {len(chunks)} chunk(s) to the database using the OpenAI embedding model.")

    except FileNotFoundError:
        print(f"[ERROR] The transcript file was not found: {TRANSCRIPT_FILE}")
    except Exception as e:
        print(f"[ERROR] An error occurred during ingestion: {e}")