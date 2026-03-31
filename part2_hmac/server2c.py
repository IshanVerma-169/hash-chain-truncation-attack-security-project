from fastapi import FastAPI, WebSocket
import hashlib
import hmac
import uvicorn

app = FastAPI()

SECRET_KEY = b"super_secret_key"

# ---------------- HMAC ----------------
def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()


# ---------------- VERIFY ----------------
def verify_chain(messages, chain, salt):
    print("\n[SERVER] 🔍 Verifying RECEIVED Chain (HMAC + SALT):")

    if len(chain) != len(messages) + 1:
        print("❌ Length mismatch!")
        return False

    for i in range(1, len(chain)):
        expected = hmac_hash(messages[i-1] + chain[i-1] + salt)

        print(f"\n  Step {i}")
        print(f"  HMAC({messages[i-1]} + prev_hash + salt)")
        print(f"  Expected: {expected[:12]}...")
        print(f"  Received: {chain[i][:12]}...")

        if expected != chain[i]:
            print("  ❌ INVALID → HMAC mismatch")
            return False

    print("\n[SERVER] ✅ Chain VALID under HMAC + SALT")
    return True


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    print("\n================ SERVER STARTED (HMAC + SALT) ================")

    # -------- FIRST MESSAGE --------
    data = await ws.receive_json()
    await ws.send_text("VALID")

    # -------- SECOND MESSAGE --------
    data = await ws.receive_json()

    messages = data["messages"]
    chain = data["chain"]
    salt = data["salt"]

    print(f"\n[SERVER] 📥 Received chain with salt: {salt}")

    if verify_chain(messages, chain, salt):
        print("\n✅ ACCEPTED (secure)")
        await ws.send_text("VALID")
    else:
        print("\n🛡️ ATTACK BLOCKED → Invalid HMAC chain")
        await ws.send_text("INVALID")


if __name__ == "__main__":
    print("🚀 Starting Server (HMAC + SALT)...")
    uvicorn.run(app, host="127.0.0.1", port=8000)