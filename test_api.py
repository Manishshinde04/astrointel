# test_api.py for OpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv

print("--- Starting OpenAI API Test ---")

# Load the .env file to get the key
load_dotenv()

# The OpenAI library automatically finds the OPENAI_API_KEY in your .env file
try:
    print("Initializing OpenAI client...")
    client = OpenAI()
    print("🟢 OpenAI client initialized successfully.")
    
    # Attempt to make an API call
    print("Attempting to generate test content...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, world."}
        ]
    )
    
    print("\n✅ --- SUCCESS! --- ✅")
    print("Your API key and connection are working correctly.")
    print("Response from OpenAI: ", response.choices[0].message.content)

except Exception as e:
    print("\n❌ --- AN ERROR OCCURRED --- ❌")
    print("The specific error is:")
    print(f"\n{e}\n")
    print("--- COMMON FIXES ---")
    print("1. Double-check that your OPENAI_API_KEY in the .env file is correct.")
    print("2. Check if your OpenAI free trial credits have expired.")
    print("3. Check your internet connection or if a firewall is blocking api.openai.com.")