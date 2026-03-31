import hashlib
import hmac
import random
import string

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

SECRET_KEY = b"super_secret_key"

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

# ---------------- RSA SETUP ----------------
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

# ---------------- RANDOM ----------------
def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

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

# ---------------- ATTACK ----------------
def attack(messages, chain):
    if len(messages) < 3:
        return messages, chain

    k = random.randint(1, len(messages) - 2)

    new_messages = messages[:-k]
    new_chain = chain[:-k]

    for fm in ["X", "Y"]:
        new_hash = hash_func(fm + new_chain[-1])
        new_chain.append(new_hash)
        new_messages.append(fm)

    return new_messages, new_chain

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

# ---------------- MULTI CHECKPOINT ----------------
def multi_checkpoint_detect(original_chain, attacked_chain):
    indices = [
        len(original_chain)//4,
        len(original_chain)//2,
        (3*len(original_chain))//4
    ]

    for i in indices:
        if i >= len(attacked_chain) or attacked_chain[i] != original_chain[i]:
            return True  # attack detected

    return False  # attack not detected

# ---------------- TEST CASES ----------------
TOTAL_TESTS = 30

attack_success = 0
checkpoint_detect = 0
hmac_prevent = 0
rsa_prevent = 0

for i in range(TOTAL_TESTS):
    n = random.randint(5, 12)
    messages = random_messages(n)
    seed = "init"

    # ---- NAIVE SYSTEM ----
    chain = build_chain(messages, seed)
    attacked_messages, attacked_chain = attack(messages, chain)

    if verify_chain(attacked_messages, attacked_chain):
        attack_success += 1

    # ---- MULTI CHECKPOINT ----
    if multi_checkpoint_detect(chain, attacked_chain):
        checkpoint_detect += 1

    # ---- HMAC SYSTEM ----
    hchain = build_hmac_chain(messages, seed)
    attacked_messages2, attacked_chain2 = attack(messages, hchain)

    if not verify_hmac(attacked_messages2, attacked_chain2):
        hmac_prevent += 1

    # ---- RSA SIGNATURE ----
    signature = sign_data(chain[-1])

    attacked_messages3, attacked_chain3 = attack(messages, chain)

    if not verify_signature(attacked_chain3[-1], signature):
        rsa_prevent += 1

# ---------------- RESULTS ----------------
attack_rate = (attack_success / TOTAL_TESTS) * 100
checkpoint_rate = (checkpoint_detect / TOTAL_TESTS) * 100
hmac_rate = (hmac_prevent / TOTAL_TESTS) * 100
rsa_rate = (rsa_prevent / TOTAL_TESTS) * 100

print("\n===== TEST CASE RESULTS =====")
print(f"Total Tests: {TOTAL_TESTS}")

print("\n--- BEFORE PREVENTION (NAIVE) ---")
print(f"Attack Success: {attack_success}/{TOTAL_TESTS}")
print(f"Success Rate: {attack_rate:.2f}%")

print("\n--- MULTI CHECKPOINT DETECTION ---")
print(f"Detected Attacks: {checkpoint_detect}/{TOTAL_TESTS}")
print(f"Detection Rate: {checkpoint_rate:.2f}%")

print("\n--- AFTER PREVENTION (HMAC) ---")
print(f"Attack Blocked: {hmac_prevent}/{TOTAL_TESTS}")
print(f"Prevention Rate: {hmac_rate:.2f}%")

print("\n--- RSA SIGNATURE PREVENTION ---")
print(f"Attack Blocked: {rsa_prevent}/{TOTAL_TESTS}")
print(f"Prevention Rate: {rsa_rate:.2f}%")