from fastapi import FastAPI, WebSocket
import websockets
import hashlib
import uvicorn
import json
import random

app = FastAPI()

SERVER_URI = "ws://127.0.0.1:8000/ws"

def fake_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def attack(messages, chain):
    print("\n[ATTACKER] ⚔️ Attempting attack WITHOUT key")

    k = random.randint(1, len(messages) - 2)

    new_messages = messages[:-k]
    new_chain = chain[:-k]

    fake_msgs = ["X", "Y"]

    for fm in fake_msgs:
        new_hash = fake_hash(fm + new_chain[-1])  # WRONG
        new_chain.append(new_hash)
        new_messages.append(fm)

    return new_messages, new_chain


@app.websocket("/ws")
async def proxy(ws_client: WebSocket):
    await ws_client.accept()

    async with websockets.connect(SERVER_URI) as ws_server:

        # pass first
        data = await ws_client.receive_text()
        await ws_server.send(data)
        resp = await ws_server.recv()
        await ws_client.send_text(resp)

        # attack second
        data = await ws_client.receive_text()
        parsed = json.loads(data)

        messages = parsed["messages"]
        chain = parsed["chain"]
        salt = parsed["salt"]

        new_messages, new_chain = attack(messages, chain)

        print("\n[ATTACKER] 🚫 Sending forged chain")

        await ws_server.send(json.dumps({
            "messages": new_messages,
            "chain": new_chain,
            "salt": salt
        }))

        resp = await ws_server.recv()
        await ws_client.send_text(resp)


if __name__ == "__main__":
    print("🚀 Starting Attacker (HMAC + SALT)...")
    uvicorn.run(app, host="127.0.0.1", port=8001)