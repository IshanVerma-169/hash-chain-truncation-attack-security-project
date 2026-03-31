from fastapi import FastAPI, WebSocket
import hashlib
import uvicorn

app = FastAPI()

# ---------------- HASH FUNCTION ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()


# ---------------- VERIFY CHAIN ----------------
def verify_chain(messages, chain):
    print("\n[SERVER] 🔍 Verifying RECEIVED Chain:")

    # Length check
    if len(chain) != len(messages) + 1:
        print("❌ Length mismatch!")
        return False

    # Step-by-step verification
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


# ---------------- WEBSOCKET ENDPOINT ----------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("\n================ SERVER STARTED (FINAL HASH PREVENTION) ================")
    print("[SERVER] Waiting for client data...")

    # -------- FIRST MESSAGE (STORE FINAL HASH) --------
    data = await ws.receive_json()

    original_messages = data["messages"]
    original_chain = data["chain"]

    print("\n[SERVER] 📥 Initial chain received")
    print("[SERVER] Messages:", original_messages)

    # Store final hash
    final_hash = original_chain[-1]
    print(f"[SERVER] 🔐 Stored Final Hash: {final_hash[:12]}...")

    # Respond like normal system
    await ws.send_text("VALID")

    # -------- SECOND MESSAGE (VERIFY + DETECT) --------
    data = await ws.receive_json()

    messages = data["messages"]
    chain = data["chain"]

    print("\n================ VERIFICATION PHASE ================")
    print("[SERVER] 📥 Received chain (may be modified)")

    is_valid = verify_chain(messages, chain)

    # Same behavior as naive system (IMPORTANT)
    if is_valid:
        print("\n⚠️ Server ACCEPTED chain based on local verification")
        await ws.send_text("VALID")
    else:
        print("\n❌ Invalid chain")
        await ws.send_text("INVALID")

    # -------- PREVENTION CHECK --------
    print("\n================ PREVENTION CHECK ================")

    if chain[-1] != final_hash:
        print("🛡️ ATTACK DETECTED: Final hash mismatch!")
    else:
        print("✅ No attack detected")


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    print("🚀 Starting Server (Final Hash Prevention)...")
    uvicorn.run(app, host="127.0.0.1", port=8000)