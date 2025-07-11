# check_env.py
from dotenv import load_dotenv
import os

# Attempt to load the .env file
load_dotenv()

# Get the key from the environment
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ Success! The API key was found in your .env file.")
else:
    print("❌ Failure! The API key was NOT found. Please double-check your .env file.")