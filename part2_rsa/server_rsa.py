from fastapi import FastAPI, WebSocket
import hashlib
import uvicorn

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

app = FastAPI()

def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def load_public_key(pem_key):
    return serialization.load_pem_public_key(pem_key.encode())

def verify_chain(messages, chain):
    print("\n[SERVER] 🔍 Verifying Chain:")

    for i in range(1, len(chain)):
        expected = hash_func(messages[i-1] + chain[i-1])

        print(f"  Step {i}")
        print(f"  Expected: {expected[:12]}...")
        print(f"  Received: {chain[i][:12]}...")

        if expected != chain[i]:
            print("  ❌ Mismatch detected")
            return False

    print("[SERVER] ✅ Chain valid")
    return True

def verify_signature(public_key, data, signature):
    print("\n[SERVER] 🔐 Verifying Signature")

    try:
        public_key.verify(
            bytes.fromhex(signature),
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("[SERVER] ✅ Signature VALID")
        return True
    except:
        print("[SERVER] ❌ Signature INVALID")
        return False

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("\n========== SERVER STARTED ==========")

    data = await ws.receive_json()

    messages = data["messages"]
    chain = data["chain"]
    signature = data["signature"]
    public_key = load_public_key(data["public_key"])

    print("[SERVER] Messages:", messages)

    if not verify_chain(messages, chain):
        await ws.send_text("INVALID_CHAIN")
        return

    if verify_signature(public_key, chain[-1], signature):
        print("[SERVER] 🟢 SECURE")
        await ws.send_text("SECURE")
    else:
        print("[SERVER] 🚨 ATTACK DETECTED")
        await ws.send_text("ATTACK_DETECTED")

if __name__ == "__main__":
    print("🚀 Server running on 8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)