import os
import io
import chromadb
import openai
import numpy as np
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, WebSocket
from pydantic import BaseModel
from scipy.io.wavfile import write as write_wav

# Define a Pydantic model for the query input
class Query(BaseModel):
    question: str

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Initialize the OpenAI client EXPLICITLY
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize a persistent ChromaDB client
db_client = chromadb.PersistentClient(path="chroma_db")
collection = db_client.get_or_create_collection(name="meeting_transcripts")


@app.post("/query-meetings")
async def query_meetings(query: Query):
    """
    This endpoint uses RAG to answer questions about past meetings.
    """
    # 1. Create an embedding for the user's question
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query.question
    )
    query_embedding = response.data[0].embedding

    # 2. Query the database for relevant context
    # We're asking for the top 3 most relevant chunks
    retrieved_chunks = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    context = "\n\n".join(retrieved_chunks['documents'][0])

    # 3. Construct the prompt with the retrieved context
    prompt = f"""
    You are a helpful meeting assistant. Based on the following context from past meetings, 
    please answer the user's question. If the context doesn't contain the answer,
    say "I don't have enough information to answer that question."

    Context:
    \"\"\"{context}\"\"\"

    Question:
    {query.question}
    """
    
    # 4. Call the GPT model to generate an answer
    answer_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    final_answer = answer_response.choices[0].message.content

    return {"answer": final_answer}


@app.post("/transcribe_and_summarize")
async def transcribe_and_summarize_audio(file: UploadFile = File(...)):
    """
    This endpoint accepts an audio file, transcribes it,
    and then generates a structured summary.
    """
    audio_bytes = await file.read()
    transcription_response = client.audio.transcriptions.create(
        model="whisper-1",
        file=(file.filename, audio_bytes)
    )
    transcript_text = transcription_response.text
    prompt = f"""
    You are a world-class meeting assistant. Your task is to generate a concise summary
    from the following meeting transcript. The summary must be structured with a
    'Key Decisions' section and an 'Action Items' section. List each item with the
    assigned owner if one is mentioned.

    Transcript:
    \"\"\"{transcript_text}\"\"\"
    """
    summary_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    summary_text = summary_response.choices[0].message.content
    return {
        "transcription": transcript_text,
        "summary": summary_text
    }


@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    """
    This WebSocket endpoint receives live audio chunks, buffers them,
    transcribes them using Whisper, and sends the transcript back.
    """
    await websocket.accept()
    print("WebSocket connection established.")
    audio_buffer = []
    BUFFER_SIZE_SAMPLES = 16000 * 5  # 5 seconds of audio

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer.append(data)
            
            current_buffer_size_bytes = sum(len(chunk) for chunk in audio_buffer)
            current_buffer_size_samples = current_buffer_size_bytes // 2
            
            if current_buffer_size_samples < BUFFER_SIZE_SAMPLES:
                continue

            # Process the buffer
            full_audio_bytes = b"".join(audio_buffer)
            audio_buffer = []

            # Convert the raw bytes to a NumPy array
            audio_np = np.frombuffer(full_audio_bytes, dtype=np.int16)

            # Create an in-memory WAV file
            byte_buffer = io.BytesIO()
            write_wav(byte_buffer, 16000, audio_np)
            wav_bytes = byte_buffer.getvalue()
            
            # Transcribe using Whisper, sending the complete WAV file bytes
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=("temp.wav", wav_bytes, "audio/wav")
            )
            
            # Print and send the transcript back to the client
            print("Transcript:", transcription.text)
            await websocket.send_text(transcription.text)

    except Exception as e:
        print("An unexpected error occurred.")
        traceback.print_exc()

    finally:
        print("WebSocket connection closed.")