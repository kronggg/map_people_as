from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    phone_hash: str
    full_name: str
    city: str
    lat: float
    lon: float