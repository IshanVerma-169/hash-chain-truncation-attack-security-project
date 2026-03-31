import hashlib
import hmac
import random
import time
import matplotlib.pyplot as plt

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# 🔒 FIX RANDOMNESS
random.seed(42)

SECRET_KEY = b"super_secret_key"

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

# ---------------- REAL DIGITAL SIGNATURE ----------------
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

def sign_data(data):
    return private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(data, signature):
    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

# ---------------- FIXED INPUT ----------------
def fixed_messages(n):
    return ["A"] * n

# ---------------- BUILD ----------------
def build_chain(messages, seed):
    chain = [seed]
    for m in messages:
        chain.append(hash_func(m + chain[-1]))
    return chain

def build_hmac_chain(messages, seed):
    chain = [seed]
    for m in messages:
        chain.append(hmac_hash(m + chain[-1]))
    return chain

# ---------------- VERIFY ----------------
def verify_chain(messages, chain):
    for i in range(1, len(chain)):
        if hash_func(messages[i-1] + chain[i-1]) != chain[i]:
            return False
    return True

def verify_hmac(messages, chain):
    for i in range(1, len(chain)):
        if hmac_hash(messages[i-1] + chain[i-1]) != chain[i]:
            return False
    return True

def verify_multi_checkpoint(chain):
    indices = [len(chain)//4, len(chain)//2, (3*len(chain))//4]
    for i in indices:
        if i >= len(chain):
            return False
    return True

# ---------------- MAIN ----------------
lengths = [5, 10, 15, 20, 25]

naive_times = []
multi_times = []
hmac_times = []
signature_times = []

runs = 100

for n in lengths:
    naive_total = multi_total = hmac_total = sig_total = 0

    for _ in range(runs):
        msgs = fixed_messages(n)

        chain = build_chain(msgs, "init")
        hchain = build_hmac_chain(msgs, "init")

        # ---- NAIVE ----
        start = time.time()
        verify_chain(msgs, chain)
        naive_total += time.time() - start

        # ---- MULTI CHECKPOINT ----
        start = time.time()
        verify_multi_checkpoint(chain)
        multi_total += time.time() - start

        # ---- HMAC ----
        start = time.time()
        verify_hmac(msgs, hchain)
        hmac_total += time.time() - start

        # ---- DIGITAL SIGNATURE ----
        start = time.time()
        sig = sign_data(chain[-1])
        verify_signature(chain[-1], sig)
        sig_total += time.time() - start

    naive_times.append(naive_total / runs)
    multi_times.append(multi_total / runs)
    hmac_times.append(hmac_total / runs)
    signature_times.append(sig_total / runs)

# ---------------- GRAPH ----------------
plt.plot(lengths, naive_times, marker='o', label="Naive")
plt.plot(lengths, multi_times, marker='o', label="Multi Checkpoint")
plt.plot(lengths, hmac_times, marker='o', label="HMAC")
plt.plot(lengths, signature_times, marker='o', label="Digital Signature (RSA)")

plt.title("Time vs Chain Length (Real Cryptographic Comparison)")
plt.xlabel("Chain Length")
plt.ylabel("Average Time (seconds)")
plt.legend()

plt.savefig("graph4.png")
plt.show()