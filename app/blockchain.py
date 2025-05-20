import hashlib
import time
from typing import List, Dict


class Block:
    def __init__(self, index: int, data: Dict, previous_hash: str = ""):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        content = f"{self.index}{self.data}{self.previous_hash}{self.timestamp}".encode()
        return hashlib.sha256(content).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, {"data": "LunaLynx12"}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data: Dict):
        latest = self.get_latest_block()
        new_block = Block(latest.index + 1, data, latest.hash)
        self.chain.append(new_block)

    def to_dict(self):
        return [b.__dict__ for b in self.chain]