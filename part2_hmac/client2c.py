import asyncio
import websockets
import hashlib
import hmac
import json
import random
import string

SERVER_URI = "ws://127.0.0.1:8001/ws"
SECRET_KEY = b"super_secret_key"

# ---------------- HMAC ----------------
def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

# ---------------- RANDOM ----------------
def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

# ---------------- SALT ----------------
def generate_salt():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# ---------------- BUILD ----------------
def build_chain(messages, seed, salt):
    print("\n[CLIENT] ⚙️ Building HMAC + SALT Chain:")
    print(f"[CLIENT] 🔑 Salt used: {salt}")

    chain = [seed]
    print(f"  Seed: {seed}")

    for i, m in enumerate(messages):
        new_hash = hmac_hash(m + chain[-1] + salt)
        print(f"  Step {i+1}: HMAC({m} + prev_hash + salt) → {new_hash[:12]}...")
        chain.append(new_hash)

    print("\n[CLIENT] ✅ Chain Generated\n")
    return chain


async def run_client():
    print("\n===== INPUT MODE =====")
    print("1. Manual Input")
    print("2. Fully Random")

    choice = input("Choose option: ")

    if choice == "1":
        messages = input("Enter messages: ").split()
    else:
        n = random.randint(3, 10)
        print(f"[CLIENT] 🎲 Random length: {n}")
        messages = random_messages(n)

    seed = input("Enter seed: ")

    salt = generate_salt()

    print("[CLIENT] Messages:", messages)

    chain = build_chain(messages, seed, salt)

    async with websockets.connect(SERVER_URI) as ws:
        print("[CLIENT] 📤 Sending ORIGINAL chain...\n")

        await ws.send(json.dumps({
            "messages": messages,
            "chain": chain,
            "salt": salt
        }))

        print("[SERVER RESPONSE]:", await ws.recv())

        print("\n[CLIENT] ⏳ Sending next request...\n")

        await ws.send(json.dumps({
            "messages": messages,
            "chain": chain,
            "salt": salt
        }))

        print("[SERVER RESPONSE]:", await ws.recv())


if __name__ == "__main__":
    asyncio.run(run_client())