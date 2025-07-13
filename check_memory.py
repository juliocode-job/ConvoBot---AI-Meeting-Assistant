# check_memory.py
import chromadb

# --- IMPORTANT ---
# This path MUST be the same one used in your other scripts.
DB_PATH = "./chroma_db"

def check_database_contents():
    """
    Connects to the persistent ChromaDB and prints its contents to verify ingestion.
    """
    print(f"Attempting to connect to database at: {DB_PATH}")
    try:
        # Connect to the same persistent database
        client = chromadb.PersistentClient(path=DB_PATH)
        
        # Get the specific collection
        collection = client.get_collection(name="meeting_transcripts")
        
        print("\nConnection successful!")
        
        # Retrieve all items from the collection
        results = collection.get() # This gets everything
        
        count = collection.count()
        
        if count == 0:
            print("\n[RESULT] The 'meeting_transcripts' collection is EMPTY.")
            print("This means the ingestion script is not saving data persistently.")
        else:
            print(f"\n[RESULT] Success! Found {count} document(s) in the collection.")
            print("Here is the data stored in the database:")
            # Print out the documents to see what was stored
            for doc in results['documents']:
                print(f"- {doc[:100]}...") # Print first 100 chars of each doc

    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        print("This could mean the collection doesn't exist or the path is wrong.")

if __name__ == "__main__":
    check_database_contents()