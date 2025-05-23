import requests
import time

BLOCKCHAIN_URL = "http://localhost:8000"
MINER_NAME = "Alex"
MINE_INTERVAL = 15          # seconds between mining attempts
API_KEY = "dummy_api_key"   # Replace this with the actual API key

session = requests.Session()

def mine_block():
    print(f"⛏️  Starting miner: {MINER_NAME}")
    backoff = 5
    headers = {"Authorization": API_KEY}  

    try:
        while True:
            try:
                response = session.get(f"{BLOCKCHAIN_URL}/mine", params={"name": MINER_NAME}, headers=headers, timeout=10)
                if response.status_code == 200:
                    print("✅", response.json().get("status"))
                    time.sleep(MINE_INTERVAL)
                    backoff = 5
                else:
                    print("❌ Mine failed, status:", response.status_code)
                    print("⏳ Retrying in", backoff, "seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff + 5, 60)
            except requests.exceptions.RequestException as e:
                print("🚫 Connection error:", e)
                print("⏳ Retrying in", backoff, "seconds...")
                time.sleep(backoff)
                backoff = min(backoff + 5, 60)
    except KeyboardInterrupt:
        print("\n🛑 Miner stopped manually. Goodbye.")

if __name__ == "__main__":
    mine_block()
