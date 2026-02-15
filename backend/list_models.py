from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Available models:")
for model in client.models.list():
    print(f"  - {model.name}")
