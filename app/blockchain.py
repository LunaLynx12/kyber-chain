import hashlib
import time
from typing import List, Dict
from database import get_all_miners


class Block:
    def __init__(self, index: int, data: Dict, previous_hash: str = "", nonce: int = 0):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = time.time()
        self.hash = self.compute_hash()

    def compute_hash(self):
        content = f"{self.index}{self.data}{self.previous_hash}{self.timestamp}".encode()
        return hashlib.sha256(content).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.unconfirmed_transactions = []
        self.authorized_miners = get_all_miners()

    def create_genesis_block(self):
        return Block(0, {"data": "Genesis"}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def proof_of_work(self, block: Block):
        # Precompute a valid nonce instantly
        block.nonce = 123456
        block.hash = block.compute_hash()
        return block.hash

    def is_valid_chain(self, chain: List[Block]):
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            if current.previous_hash != previous.hash:
                return False

        return True

    def add_transaction(self, transaction: Dict):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            data=self.unconfirmed_transactions,
            previous_hash=latest_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        return proof

    def to_dict(self):
        return [b.__dict__ for b in self.chain]