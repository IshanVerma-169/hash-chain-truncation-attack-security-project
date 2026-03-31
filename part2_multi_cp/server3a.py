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

    if len(chain) != len(messages) + 1:
        print("❌ Length mismatch!")
        return False

    for i in range(1, len(chain)):
        expected = hash_func(messages[i-1] + chain[i-1])

        print(f"\n  Step {i}")
        print(f"  Expected: {expected[:12]}...")
        print(f"  Received: {chain[i][:12]}...")

        if expected != chain[i]:
            print("  ❌ Mismatch detected")
            return False

    print("\n[SERVER] ✅ Local consistency PASSED")
    return True


# ---------------- WEBSOCKET ----------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("\n================ SERVER STARTED (MULTI CHECKPOINT) ================")

    # -------- FIRST MESSAGE --------
    data = await ws.receive_json()
    original_messages = data["messages"]
    original_chain = data["chain"]

    print("\n[SERVER] 📥 Initial chain received")
    print(f"[SERVER] Original Chain Length: {len(original_chain)}")

    # -------- STORE MULTIPLE CHECKPOINTS --------
    n = len(original_chain)

    checkpoint_indices = [
        n // 4,
        n // 2,
        (3 * n) // 4
    ]

    checkpoints = {i: original_chain[i] for i in checkpoint_indices}

    print("\n[SERVER] 🔐 Stored Checkpoints:")
    for idx in checkpoint_indices:
        print(f"  Index {idx}: {checkpoints[idx][:12]}...")

    await ws.send_text("VALID")

    # -------- SECOND MESSAGE --------
    data = await ws.receive_json()
    messages = data["messages"]
    chain = data["chain"]

    print("\n================ VERIFICATION PHASE ================")
    print("[SERVER] 📥 Received chain (may be attacked)")
    print(f"[SERVER] Received Chain Length: {len(chain)}")

    is_valid = verify_chain(messages, chain)

    # -------- NAIVE ACCEPTANCE --------
    if is_valid:
        print("\n⚠️ Server ACCEPTED chain (local check)")
        await ws.send_text("VALID")
    else:
        print("\n❌ Invalid chain")
        await ws.send_text("INVALID")

    # -------- MULTI-CHECKPOINT DETECTION --------
    print("\n================ MULTI-CHECKPOINT VALIDATION ================")

    detected = False

    # ---- LENGTH CHECK ----
    if len(chain) != len(original_chain):
        print("🛡️ ATTACK DETECTED: Chain length mismatch!")
        detected = True

    # ---- CHECKPOINT VALIDATION ----
    for idx in checkpoint_indices:
        if idx >= len(chain):
            print(f"🛡️ ATTACK DETECTED: Missing checkpoint at index {idx}")
            detected = True
        elif chain[idx] != checkpoints[idx]:
            print(f"🛡️ ATTACK DETECTED at checkpoint index {idx}")
            detected = True

    # ---- FINAL RESULT ----
    if not detected:
        print("⚠️ No checkpoint mismatch → attack bypassed")


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    print("🚀 Starting Server (Multi Checkpoint)...")
    uvicorn.run(app, host="127.0.0.1", port=8000)