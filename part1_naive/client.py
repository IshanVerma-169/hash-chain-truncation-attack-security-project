import asyncio
import websockets
import hashlib
import json
import random
import string

SERVER_URI = "ws://127.0.0.1:8001/ws"

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------- RANDOM ----------------
def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

# ---------------- BUILD CHAIN ----------------
def build_chain(messages, seed):
    print("\n[CLIENT] ⚙️ Building Hash Chain:")

    chain = [seed]
    print(f"  Seed: {seed}")

    for i, m in enumerate(messages):
        new_hash = hash_func(m + chain[-1])
        print(f"  Step {i+1}: H({m} + {chain[-1][:8]}...) → {new_hash[:12]}...")
        chain.append(new_hash)

    print("\n[CLIENT] ✅ Chain Generated Successfully\n")
    return chain

async def run_client():
    print("\n===== INPUT MODE =====")
    print("1. Manual Input")
    print("2. Fully Random (length + messages)")

    choice = input("Choose option: ")

    if choice == "1":
        messages = input("Enter messages (space separated): ").split()
    else:
        n = random.randint(3, 10)
        print(f"[CLIENT] 🎲 Random message length chosen: {n}")
        messages = random_messages(n)

    seed = input("Enter seed: ")

    print("[CLIENT] Messages:", messages)

    chain = build_chain(messages, seed)

    async with websockets.connect(SERVER_URI) as ws:
        print("[CLIENT] 📤 Sending ORIGINAL chain...\n")

        await ws.send(json.dumps({
            "messages": messages,
            "chain": chain
        }))

        response = await ws.recv()
        print("[SERVER RESPONSE]:", response)

        # 👇 cleaned message (no mention of attack)
        print("\n[CLIENT] ⏳ Sending next request...\n")

        await ws.send(json.dumps({
            "messages": messages,
            "chain": chain
        }))

        response = await ws.recv()
        print("[SERVER RESPONSE]:", response)


if __name__ == "__main__":
    print("🚀 Starting Client...")
    asyncio.run(run_client())