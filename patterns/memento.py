from typing import Optional, List
from models.models_users import User, UserPublic

def snapshot_user(u: User) -> UserPublic:
    return UserPublic(id=u.id, name=u.name, email=u.email, role=u.role, status=u.status)

class _Caretaker:
    def __init__(self) -> None:
        self._stack: List[UserPublic] = []
    def save(self, m: UserPublic) -> None:
        self._stack.append(m)
    def pop(self) -> Optional[UserPublic]:
        return self._stack.pop() if self._stack else None

UserMementoCaretaker = _Caretaker()
