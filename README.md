# 🔐 Hash Chain Security Project  
### Truncation/Rebinding Attack & Prevention (HMAC, RSA, Checkpoints)

---

## 📌 Overview

This project demonstrates vulnerabilities in hash chain-based systems and implements multiple prevention mechanisms.

We simulate a *Client → Attacker → Server* architecture where:
- The attacker performs a *rebinding attack*
- The naive system fails
- Security mechanisms (HMAC, RSA) prevent the attack

---

## ⚙️ Required Software Installations

Make sure the following are installed:

### 🐍 Python
- Python 3.8 or above  
- Download: https://www.python.org/downloads/

### 📦 Required Libraries

Run the following command:

```bash
pip install fastapi uvicorn websockets cryptography


---

📁 Project Structure

cry-project/
│
├── part1_naive/
│   ├── server.py
│   ├── attacker.py
│   ├── client.py
│
├── part2_hmac/
│   ├── server.py
│   ├── attacker.py
│   ├── client.py
│
├── part2_rsa/
│   ├── server_rsa.py
│   ├── attacker_rsa.py
│   ├── client_rsa.py
│
├── graphs/
│   ├── graph1.py
│   ├── graph2.py
│   ├── graph3.py
│   ├── graph4.py
│
├── testcases.py
└── README.md


---

🚀 Step-by-Step Execution Process

⚠️ IMPORTANT: Always follow the order below


---

🟢 Step 1: Start Server

python server.py

(or for RSA)

python server_rsa.py


---

🟢 Step 2: Start Attacker

Open a new terminal:

python attacker.py

(or)

python attacker_rsa.py


---

🟢 Step 3: Run Client

Open another terminal:

python client.py

(or)

python client_rsa.py


---

▶️ Instructions to Run the Project


---

🔴 1. Naive System (Attack Successful)

cd part1_naive
python server.py
python attacker.py
python client.py

Expected Output:

ATTACK SUCCESS


---

🟡 2. HMAC System (Attack Prevented)

cd part2_hmac
python server.py
python attacker.py
python client.py

Expected Output:

ATTACK DETECTED / SECURE


---

🔵 3. RSA System (Strongest Protection)

cd part2_rsa
python server_rsa.py
python attacker_rsa.py
python client_rsa.py

Expected Output:

ATTACK DETECTED


---

📊 Running Graphs

Navigate to the graphs folder:

cd graphs
python graph1.py
python graph2.py
python graph3.py
python graph4.py


---

🧪 Running Test Cases

python testcases.py


---

🧠 Key Concepts Demonstrated

Hash Chain Integrity vs Authentication

Rebinding Attack (Structural Attack)

HMAC-based Protection

RSA Digital Signature Verification

Checkpoint-based Detection



---

📌 Notes

Ensure ports are not already in use:

Server → 8002

Attacker → 8003


Always run in correct order:

Server → Attacker → Client



---

👨‍💻 Authors

Ishan Verma - 23BAI1198
Amar Singh - 23BAI1139
Soham Sinha - 23BAI1223

---

📄 License

This project is for academic purposes only.

---
