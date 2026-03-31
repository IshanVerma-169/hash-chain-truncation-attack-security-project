import hashlib
import hmac
import random
import string
import matplotlib.pyplot as plt

SECRET_KEY = b"super_secret_key"

def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hmac_hash(data):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

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

# ---------------- MAIN ----------------
tests = 50

naive = final = single = multi = hmac_val = 0

for _ in range(tests):
    n = random.randint(6, 15)
    msgs = random_messages(n)

    chain = build_chain(msgs, "init")
    am, ac = attack(msgs, chain)

    if verify_chain(am, ac):
        naive += 1

    if verify_chain(am, ac) and ac[-1] == chain[-1]:
        final += 1

    idx = len(chain)//2
    if verify_chain(am, ac):
        if len(ac) > idx and ac[idx] == chain[idx]:
            single += 1

    indices = [len(chain)//4, len(chain)//2, (3*len(chain))//4]
    if verify_chain(am, ac):
        if all(len(ac) > i and ac[i] == chain[i] for i in indices):
            multi += 1

    hchain = build_hmac_chain(msgs, "init")
    am2, ac2 = attack(msgs, hchain)
    if verify_hmac(am2, ac2):
        hmac_val += 1

values = [naive, final, single, multi, hmac_val]
values = [(v/tests)*100 for v in values]

plt.bar(["Naive","Final","Single CP","Multi CP","HMAC"], values)
plt.title("Undetected Attack Rate")
plt.ylabel("Percentage")
plt.savefig("graph1.png")
plt.show()