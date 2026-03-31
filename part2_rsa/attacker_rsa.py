from fastapi import FastAPI, WebSocket
import hashlib
import uvicorn
import json
import websockets

app = FastAPI()

SERVER_URI = "ws://127.0.0.1:8002/ws"

def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

@app.websocket("/ws")
async def attacker(ws: WebSocket):
    await ws.accept()

    print("\n========== ATTACKER STARTED ==========")

    data = await ws.receive_json()

    messages = data["messages"]
    chain = data["chain"]
    signature = data["signature"]
    public_key = data["public_key"]

    print("[ATTACKER] Original Messages:", messages)

    # -------- ATTACK --------
    print("\n[ATTACKER] ⚔️ Rebinding Attack")

    new_messages = messages[:-1]
    new_chain = chain[:-1]

    fake = "X"
    new_hash = hash_func(fake + new_chain[-1])

    new_messages.append(fake)
    new_chain.append(new_hash)

    print("[ATTACKER] Modified Messages:", new_messages)

    forged_data = {
        "messages": new_messages,
        "chain": new_chain,
        "signature": signature,  # cannot recompute
        "public_key": public_key
    }

    print("[ATTACKER] Forwarding to Server...")

    async with websockets.connect(SERVER_URI) as server_ws:
        await server_ws.send(json.dumps(forged_data))
        response = await server_ws.recv()

    print("[ATTACKER] Server Response:", response)

    await ws.send_text(response)

if __name__ == "__main__":
    print("🚀 Attacker running on 8003")
    uvicorn.run(app, host="127.0.0.1", port=8003)