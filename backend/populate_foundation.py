import os
import grpc
import vdss_pb2
import vdss_pb2_grpc
from dotenv import load_dotenv
from google import genai

# 1. Environment Sync
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Material Library (Semantic Data for Aetheris OS)
materials = [
    {"name": "Photochromic-A1", "desc": "High UV reactivity, liquid-cooled, ideal for desert climates."},
    {"name": "Thermo-Tint-B2", "desc": "Heat-activated shading, low thermal expansion, high durability."},
    {"name": "Electro-Polymer-C3", "desc": "Voltage-controlled opacity, ultra-low power consumption for summer cooling."},
    {"name": "Aether-Graphene-X", "desc": "Conductive thermal mass, optimized for server heat absorption in cold weather."}
]

def build_local_index():
    # Connect to the Active Foundation (Actian container)
    channel = grpc.insecure_channel('127.0.0.1:50051')
    stub = vdss_pb2_grpc.VDSSServiceStub(channel)

    print("--- [AETHERIS OS] Starting Sustainable Bulk Embedding ---")
    print(f"Targeting Local Foundation at 127.0.0.1:50051")

    for item in materials:
        try:
            # Use 300$ Credits to get 3072-dim embeddings
            # We use gemini-embedding-001 as it's the stable SKU for your tier
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=item["desc"]
            )
            vector_data = result.embeddings[0].values

            # Push to local FAISS index
            upsert_req = vdss_pb2.UpsertVectorRequest(
                collection_name="materials",
                vector=vdss_pb2.Vector(data=vector_data, dimension=3072)
            )
            
            stub.UpsertVector(upsert_req)
            print(f"✅ [STORED] {item['name']} localized to HP Envy")

        except Exception as e:
            print(f"❌ [FAILED] {item['name']}: {str(e)}")

if __name__ == "__main__":
    build_local_index()
