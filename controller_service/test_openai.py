import os
from openai import OpenAI

# Set the API key
# IMPORTANT: Never hardcode API keys in your code
# Use environment variables or secure configuration methods
api_key = os.environ.get("OPENAI_API_KEY", "your-api-key-here")

# Check if API key is provided
if api_key == "your-api-key-here":
    print("WARNING: No OpenAI API key provided. Set the OPENAI_API_KEY environment variable.")
    print("This test will not work without a valid API key.")
    exit(1)

# Initialize the client
client = OpenAI(api_key=api_key)

# Test the API
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ]
    )
    print("API Response:")
    print(response.choices[0].message.content)
    print("\nAPI is working correctly!")
except Exception as e:
    print(f"Error: {str(e)}") 