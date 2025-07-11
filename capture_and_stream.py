# capture_and_stream.py
import asyncio
import websockets
import sounddevice as sd

# --- Configuration ---
DEVICE_INDEX = 2 
CHANNELS = 1
SAMPLE_RATE = 16000
WEBSOCKET_URI = "ws://127.0.0.1:8000/ws/transcribe"

async def audio_streamer():
    """Captures audio and streams it, while also printing responses."""
    
    audio_queue = asyncio.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue.put_nowait(indata.copy())

    # This task sends audio from the queue to the server
    async def sender(websocket):
        print("Sender task started.")
        while True:
            data = await audio_queue.get()
            await websocket.send(data.tobytes())
            audio_queue.task_done()

    # This task receives and prints messages from the server
    async def receiver(websocket):
        print("Receiver task started.")
        while True:
            transcript = await websocket.recv()
            print(f"Live Transcript: {transcript}")

    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print("Connected to WebSocket server.")
            
            # Create and start the sender and receiver tasks
            sender_task = asyncio.create_task(sender(websocket))
            receiver_task = asyncio.create_task(receiver(websocket))
            
            with sd.InputStream(samplerate=SAMPLE_RATE, 
                                 channels=CHANNELS, 
                                 dtype='int16', 
                                 device=DEVICE_INDEX, 
                                 callback=callback):
                
                print(f"Streaming audio from device {DEVICE_INDEX}...")
                # Wait for both tasks to complete (which they won't, they run forever)
                await asyncio.gather(sender_task, receiver_task)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting audio streamer...")
    try:
        asyncio.run(audio_streamer())
    except KeyboardInterrupt:
        print("\nAudio streamer stopped.")