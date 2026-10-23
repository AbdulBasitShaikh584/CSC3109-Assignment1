"""Generate three API keys. Run once; keys are printed ONCE and only their
SHA-256 hashes are stored in keys.json (which is git-ignored)."""
import hashlib, json, secrets

consumers = ["tester_1", "tester_2", "tester_3"]
store = {}
for c in consumers:
    key = secrets.token_urlsafe(32)
    store[hashlib.sha256(key.encode()).hexdigest()] = c
    print(f"{c}: {key}")

with open("keys.json", "w") as f:
    json.dump(store, f, indent=2)
print("\nSend each key privately to its tester. Do NOT commit keys.json or these keys.")
