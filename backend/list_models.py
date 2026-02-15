from google import genai

client = genai.Client(api_key="REDACTED_API_KEYSyDK0KHwAvgpEif3DSE3MJ6T-Wp8w8sKypY")

print("Available models:")
for model in client.models.list():
    print(f"  - {model.name}")
