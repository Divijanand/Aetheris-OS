from services.gemini import embed_text

vec = embed_text("SIPS panel for high thermal efficiency modular home")
print("Vector length:", len(vec))
print(vec[:10])
