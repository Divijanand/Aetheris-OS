#!/usr/bin/env python3
import os, json, shlex, subprocess
from dotenv import load_dotenv
load_dotenv()
from services.gemini import embed_text

ACTIAN_ADDR = os.getenv("ACTIAN_ADDR", "localhost:50051")
COLLECTION = "materials"
DIM = 3072

def make_search_request(query_text, top_k=5):
    vec = embed_text(query_text)
    payload = {
        "collection_name": COLLECTION,
        "query": {"data": vec, "dimension": len(vec)},
        "top_k": int(top_k),
        "with_vector": False,
        "with_payload": True
    }
    return payload

def run_search(req):
    tmp = "/tmp/aetheris_search.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(req, f)
    cmd = f"grpcurl -plaintext -d @{shlex.quote(tmp)} {ACTIAN_ADDR} vdss.VDSSService/Search"
    res = subprocess.check_output(cmd, shell=True, text=True)
    try:
        parsed = json.loads(res)
        print(json.dumps(parsed, indent=2))
    except Exception:
        print("Raw response:")
        print(res)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python app/search_materials.py \"your query text\" [top_k]")
        sys.exit(1)
    q = sys.argv[1]
    k = sys.argv[2] if len(sys.argv) > 2 else 5
    req = make_search_request(q, k)
    run_search(req)
