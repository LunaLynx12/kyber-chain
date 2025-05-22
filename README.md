## Decentralized blockchain-based chat app using post-quantum cryptography
This is a Python-based blockchain project that integrates post-quantum key exchange algorithms (ML-KEM and CRYSTALS-Kyber) using the Kyber-Python library.

```mermaid
flowchart TD
    subgraph Blockchain
        BC[(Smart Contracts)]
        BC -->|Validation| Node1
        BC -->|Validation| Node2
    end

    subgraph Phone1["📱 Phone A (Peer 1)"]
        Wallet1["🔐 Wallet (Decentralized Identity)"]
        App1["🛠️ Web3 frontend"]
        Keys1["🔑 ML-KEM Keys"]
    end

    subgraph Phone2["📱 Phone B (Peer 2)"]
        Wallet2["🔐 Wallet (Decentralized Identity)"]
        App2["🛠️ Web3 frontend"]
        Keys2["🔑 ML-KEM Keys"]
    end

    Phone1 -->|Establish P2P Connection| Phone2
    Phone1 -->|Key Exchange Kyber/KEM| Phone2
    Phone1 -->|Encrypted Data| Phone2
    Phone1 -->|Validate Transaction  on-chain| Blockchain
    Phone2 -->|Validate Transaction  on-chain| Blockchain
```

Proof of Work (PoW) is a great concept for decentralization and security , but it's also computationally expensive and can be very slow. For that reason, i chose to implement Proof of Authority (PoA)

[Wikipedia Proof-of-authority](https://en.wikipedia.org/wiki/Proof_of_authority)

| Feature                                                       | Status |
| :------------------------------------------------------------ | :----: |
| Only real users can send messages                             | Yes    |
| Miners can’t forge or alter transactions                      | Yes    |
| Proof of Authority ensures only trusted miners can mine       | Yes    |
| Secure against fake transactions                              | No     |