import asyncio
import websockets
import hashlib
import json
import random
import string

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

SERVER_URI = "ws://127.0.0.1:8003/ws"

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

def build_chain(messages, seed):
    chain = [seed]

    print("\n[CLIENT] Building Chain:")

    for i, m in enumerate(messages):
        new_hash = hash_func(m + chain[-1])
        chain.append(new_hash)

        print(f"  Step {i+1}: {new_hash[:12]}...")

    return chain

def sign_data(data):
    print("[CLIENT] Signing Final Hash")

    return private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    ).hex()

def get_public_key():
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

async def run_client():
    n = random.randint(5, 10)
    messages = random_messages(n)
    seed = "init"

    print("[CLIENT] Messages:", messages)

    chain = build_chain(messages, seed)
    signature = sign_data(chain[-1])

    async with websockets.connect(SERVER_URI) as ws:
        print("\n[CLIENT] Sending to Attacker...")

        await ws.send(json.dumps({
            "messages": messages,
            "chain": chain,
            "signature": signature,
            "public_key": get_public_key()
        }))

        response = await ws.recv()
        print("\n[CLIENT] Final Response:", response)

if __name__ == "__main__":
    asyncio.run(run_client())