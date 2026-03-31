from fastapi import FastAPI, WebSocket
import hashlib
import uvicorn

app = FastAPI()

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------- VERIFY ----------------
def verify_chain(messages, chain):
    print("\n[SERVER] 🔍 Verifying RECEIVED Chain:")

    if len(chain) != len(messages) + 1:
        print("❌ Length mismatch!")
        return False

    for i in range(1, len(chain)):
        expected = hash_func(messages[i-1] + chain[i-1])

        print(f"\n  Step {i}")
        print(f"  H({messages[i-1]} + prev_hash)")
        print(f"  Expected: {expected[:12]}...")
        print(f"  Received: {chain[i][:12]}...")

        if expected != chain[i]:
            print("  ❌ Mismatch detected")
            return False

    print("\n[SERVER] ✅ Local consistency PASSED")
    return True


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("\n================ SERVER STARTED (NAIVE) ================")

    # -------- FIRST MESSAGE (STORE ONLY, NO PRINT) --------
    data = await ws.receive_json()
    original_messages = data["messages"]
    original_chain = data["chain"]

    # silently accept
    await ws.send_text("VALID")

    # -------- SECOND MESSAGE (REAL VERIFICATION) --------
    data = await ws.receive_json()
    messages = data["messages"]
    chain = data["chain"]

    print("\n================ VERIFICATION PHASE ================")
    print("[SERVER] 📥 Received chain (may be original or attacked)")

    if verify_chain(messages, chain):
        print("\n🚨 NOTE: Server ACCEPTED the received chain")
        await ws.send_text("VALID")
    else:
        print("\n❌ Invalid chain")
        await ws.send_text("INVALID")


if __name__ == "__main__":
    print("🚀 Starting Naive Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)