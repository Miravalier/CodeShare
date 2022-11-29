from __future__ import annotations
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    hashed_password: bytes
