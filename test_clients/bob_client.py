import requests

BASE_URL = "http://localhost:8000"

if __name__ == "__main__":
    print("Bob receives message...")
    response = requests.get(f"{BASE_URL}/chain")
    chain = response.json()
    
    # Get the latest message block
    latest_block = chain[-1]
    encrypted_data = latest_block["data"]["encrypted_data"]

    # Since we're using plaintext now, just print the ciphertext directly
    print(f"Received:", encrypted_data["ciphertext"])