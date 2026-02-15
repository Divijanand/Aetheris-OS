#!/usr/bin/env python3
"""
Embed materials_seed.json with Gemini, write BatchUpsert JSON, and send to Actian via grpcurl.
Run from ~/aetheris-os/backend with venv active:
  source venv/bin/activate
  python app/upsert_materials.py
"""
import os, json, shlex, subprocess
from dotenv import load_dotenv
load_dotenv()

from services.gemini import embed_text

ROOT = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_FILE = os.path.join(ROOT, "data", "materials_seed.json")
OUT_FILE = os.path.join(ROOT, "batch_upsert.json")
ACTIAN_ADDR = os.getenv("ACTIAN_ADDR", "localhost:50051")
COLLECTION = "materials"
DIM = 3072

def load_materials():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_batch_request(materials):
    vector_ids = []
    vectors = []
    payloads = []

    for m in materials:
        mid = m.get("id") or m.get("name")
        text = m.get("text") or m.get("description") or m.get("name")
        print("Embedding:", mid)
        vec = embed_text(text)
        if not isinstance(vec, list):
            raise RuntimeError("embed_text() must return a list of floats")
        vector_ids.append({"uuid": str(mid)})
        vectors.append({"data": vec, "dimension": len(vec)})
        payloads.append({"json": json.dumps(m)})
    return {
        "collection_name": COLLECTION,
        "vector_ids": vector_ids,
        "vectors": vectors,
        "payloads": payloads
    }

def write_and_send(req):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(req, f, ensure_ascii=False)
    print(f"Wrote batch payload to {OUT_FILE} ({len(req['vectors'])} vectors).")
    cmd = f"grpcurl -plaintext -d @{shlex.quote(OUT_FILE)} {ACTIAN_ADDR} vdss.VDSSService/BatchUpsert"
    print("Calling Actian to upsert (this may take a moment)...")
    subprocess.check_call(cmd, shell=True)

def main():
    mats = load_materials()
    req = build_batch_request(mats)
    write_and_send(req)
    print("Done. Verifying vector count:")
    subprocess.check_call(f"grpcurl -plaintext -d '{{\"collection_name\":\"{COLLECTION}\"}}' {ACTIAN_ADDR} vdss.VDSSService/GetVectorCount", shell=True)

if __name__ == "__main__":
    main()
