# ingest_memory.py
import os
import chromadb
import openai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# This now creates a persistent database on your disk
db_client = chromadb.PersistentClient(path="chroma_db") 

collection = db_client.get_or_create_collection(name="meeting_transcripts")
ai_client = openai.OpenAI()

sample_transcript = """
John: Okay team, let's kick off the Q3 planning meeting. First on the agenda is the new marketing campaign, "Project Sunrise." Maria, what's the latest?
Maria: Thanks, John. The creative team has finalized the visuals, and they look fantastic. We're on track for a launch on August 1st. However, the budget for the social media ads is tight. We need an additional $5,000 to ensure we get the reach we need.
John: An extra $5,000... I see. Can we pull that from the Q2 surplus?
Sarah: I checked this morning. Yes, we can reallocate the funds from the Q2 general budget surplus. I'll need formal approval to do that.
John: Okay, consider it approved. Sarah, please process that reallocation. Maria, you've got your extra budget. Let's make it count.
Maria: Great, thank you! That's all for Project Sunrise.
John: Perfect. Next up, the new support chatbot initiative. Peter, how are we doing?
Peter: We've hit a snag. The user testing feedback shows the bot fails to understand complex queries about billing. It's causing a lot of frustration. We need to retrain the model with a better dataset.
John: A better dataset... Where do we get that?
Peter: Sarah's team has historical support tickets. We could use those, but they need to be anonymized first to protect customer privacy. It's a significant data-cleaning task.
John: Understood. Action item for Sarah: provide Peter's team with an anonymized dataset of billing-related support tickets by the end of next week. Peter, your action item is to develop a retraining plan once you have the data.
Sarah: Understood. I'll get on it.
Peter: Sounds good.
John: Excellent. That's all for today. Great meeting, everyone.
"""

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_text(sample_transcript)
print(f"Transcript split into {len(chunks)} chunks.")

for i, chunk in enumerate(chunks):
    response = ai_client.embeddings.create(model="text-embedding-3-small", input=chunk)
    embedding = response.data[0].embedding
    collection.add(ids=[f"chunk_{i+1}"], embeddings=[embedding], documents=[chunk])
    print(f"✅ Added chunk {i+1} to the database.")

print("\n🎉 Persistent memory ingestion complete!")