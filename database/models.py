from dataclasses import dataclass

@dataclass
class UserSearchResult:
    user_id: int
    full_name: str
    nickname: str
    skills: str