import hashlib
import random
import string
import matplotlib.pyplot as plt

def hash_func(data):
    return hashlib.sha256(data.encode()).hexdigest()

def random_messages(n):
    return [''.join(random.choices(string.ascii_uppercase, k=1)) for _ in range(n)]

def build_chain(messages, seed):
    chain = [seed]
    for m in messages:
        chain.append(hash_func(m + chain[-1]))
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

# ---------------- MAIN ----------------
tests = 50

final = single = multi = 0

for _ in range(tests):
    n = random.randint(6, 15)
    msgs = random_messages(n)

    chain = build_chain(msgs, "init")
    am, ac = attack(msgs, chain)

    # final hash detection
    if ac[-1] != chain[-1]:
        final += 1

    # single checkpoint
    idx = len(chain)//2
    if len(ac) <= idx or ac[idx] != chain[idx]:
        single += 1

    # multi checkpoint
    indices = [len(chain)//4, len(chain)//2, (3*len(chain))//4]
    if any(len(ac) <= i or ac[i] != chain[i] for i in indices):
        multi += 1

values = [final, single, multi]
values = [(v/tests)*100 for v in values]

plt.bar(["Final Hash","Single CP","Multi CP"], values)
plt.title("Detection Rate")
plt.ylabel("Percentage")
plt.savefig("graph3.png")
plt.show()