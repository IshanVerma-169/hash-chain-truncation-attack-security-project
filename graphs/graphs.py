import hashlib
import hmac
import random
import string
import matplotlib.pyplot as plt

SECRET_KEY = b"super_secret_key"

# ---------------- HASH ----------------
def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

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

    fake_msgs = ["X", "Y"]

    for fm in fake_msgs:
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

# ---------------- EXPERIMENT ----------------
tests = 50

naive_undetected = 0
final_undetected = 0
single_cp_undetected = 0
multi_cp_undetected = 0
hmac_undetected = 0

for _ in range(tests):
    n = random.randint(6, 15)
    messages = random_messages(n)
    seed = "init"

    # ---- ORIGINAL ----
    chain = build_chain(messages, seed)
    attacked_messages, attacked_chain = attack(messages, chain)

    # ---- NAIVE ----
    if verify_chain(attacked_messages, attacked_chain):
        naive_undetected += 1

    # ---- FINAL HASH ----
    final_hash = chain[-1]
    if verify_chain(attacked_messages, attacked_chain):
        if attacked_chain[-1] == final_hash:
            final_undetected += 1

    # ---- SINGLE CHECKPOINT ----
    idx = len(chain) // 2
    checkpoint = chain[idx]

    if verify_chain(attacked_messages, attacked_chain):
        if len(attacked_chain) > idx and attacked_chain[idx] == checkpoint:
            single_cp_undetected += 1

    # ---- MULTI CHECKPOINT ----
    indices = [len(chain)//4, len(chain)//2, (3*len(chain))//4]
    passed_all = True

    if verify_chain(attacked_messages, attacked_chain):
        for i in indices:
            if len(attacked_chain) <= i or attacked_chain[i] != chain[i]:
                passed_all = False
                break

        if passed_all:
            multi_cp_undetected += 1

    # ---- HMAC ----
    hmac_chain = build_hmac_chain(messages, seed)
    attacked_messages2, attacked_chain2 = attack(messages, hmac_chain)

    if verify_hmac(attacked_messages2, attacked_chain2):
        hmac_undetected += 1

# ---------------- RATES ----------------
naive_rate = (naive_undetected / tests) * 100
final_rate = (final_undetected / tests) * 100
single_rate = (single_cp_undetected / tests) * 100
multi_rate = (multi_cp_undetected / tests) * 100
hmac_rate = (hmac_undetected / tests) * 100

# ---------------- GRAPH ----------------
methods = ["Naive", "Final Hash", "Single CP", "Multi CP", "HMAC"]
values = [naive_rate, final_rate, single_rate, multi_rate, hmac_rate]

plt.figure()
plt.bar(methods, values)

plt.title("Undetected Attack Rate Comparison")
plt.xlabel("Methods")
plt.ylabel("Undetected Attack (%)")

plt.savefig("undetected_attack.png")
plt.show()

# ---------------- PRINT ----------------
print("\n===== FINAL RESULTS =====")
print(f"Naive Undetected: {naive_rate:.2f}%")
print(f"Final Hash Undetected: {final_rate:.2f}%")
print(f"Single Checkpoint Undetected: {single_rate:.2f}%")
print(f"Multi Checkpoint Undetected: {multi_rate:.2f}%")
print(f"HMAC Undetected: {hmac_rate:.2f}%")