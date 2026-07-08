import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the client with OpenRouter's details
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("JDNFJCJDJSMAKXNSJSMXS"), # Or use os.environ.get("OPENROUTER_API_KEY")
)

# Call the model (use OpenRouter's model strings)
response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free", # You can use any model OpenRouter hosts
    messages=[
        {
            "role": "user",
            "content": "What are three fun facts about space?"
        }
    ],
    extra_body={"reasoning": {"enabled": True}}
)

# Extract the assistant message with reasoning_details
response = response.choices[0].message

# Preserve the assistant message with reasoning_details
messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.content,
    "reasoning_details": response.reasoning_details  # Pass back unmodified
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

# Second API call - model continues reasoning from where it left off
response2 = client.chat.completions.create(
  model="openai/gpt-oss-120b:free",
  messages=messages,
  extra_body={"reasoning": {"enabled": True}}
)

r = response2.choices[0].message

# --- FIX: Print directly from the message object ---
print("First Response Content:", r.content)