import hashlib
import time
from typing import List, Dict


class Block:
    def __init__(self, index: int, data: Dict, previous_hash: str = "", nonce: int = 0):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = time.time()
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        content = f"{self.index}{self.data}{self.previous_hash}{self.nonce}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.unconfirmed_transactions: List[Dict] = []
        self.authorized_miners: List[str] = []

    def create_genesis_block(self) -> Block:
        return Block(0, {"data": "Genesis"}, "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, block: Block) -> str:
        # Simulate mining with a fixed nonce for now
        block.nonce = 123456 # TODO: Implement a real proof of work algorithm
        block.hash = block.compute_hash()
        return block.hash

    def is_valid_chain(self, chain: List[Block]) -> bool:
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            if current.previous_hash != previous.hash:
                return False

        return True

    def add_transaction(self, transaction: Dict) -> None:
        self.unconfirmed_transactions.append(transaction)

    def mine(self) -> bool:
        if not self.unconfirmed_transactions:
            return False

        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            data=self.unconfirmed_transactions.copy(),
            previous_hash=latest_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.unconfirmed_transactions.clear()
        return True

    def set_authorized_miners(self, miners: List[str]) -> None:
        self.authorized_miners = miners

    def to_dict(self) -> List[Dict]:
        return [block.__dict__ for block in self.chain]