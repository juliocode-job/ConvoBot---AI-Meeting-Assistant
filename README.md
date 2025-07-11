# 🤖 ConvoBot - AI Meeting Assistant

An intelligent meeting assistant built with Python and OpenAI. Provides real-time transcription, structured summaries, and a searchable "collective memory" using RAG.

---

## ✨ Key Features

* **Transcription & Summarization**: Upload an audio file (`.mp3`, `.wav`, etc.) to receive a full text transcript and a structured summary with "Key Decisions" and "Action Items".
* **Real-Time Transcription**: Capture live system audio during a meeting and receive a real-time transcript via WebSockets.
* **Collective Memory (Q&A)**: After processing meetings, ask questions in natural language (e.g., "What was the decision on the Q3 budget?") and get answers based on past conversations.

---

## 🛠️ Tech Stack

* **Backend**: Python, FastAPI
* **AI Models**: OpenAI API (Whisper for transcription, GPT-4o for summarization/Q&A, text-embedding-3-small for embeddings)
* **Database**: ChromaDB (Vector Database for RAG)
* **Real-Time Communication**: WebSockets
* **Core Libraries**: LangChain (for text chunking), sounddevice, numpy, scipy

---

## 🚀 Setup and Usage

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

* Python 3.10+
* Git
* A virtual audio driver for real-time capture (e.g., [VB-CABLE](https://vb-audio.com/Cable/) for Windows, [BlackHole](https://existential.audio/blackhole/) for macOS)

### 2. Installation

Clone the repository to your local machine:
```bash
git clone [https://github.com/juliocode-job/ConvoBot---AI-Meeting-Assistant.git](https://github.com/juliocode-job/ConvoBot---AI-Meeting-Assistant.git)
cd ConvoBot---AI-Meeting-Assistant