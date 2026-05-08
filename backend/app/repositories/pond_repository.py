from typing import Optional, List
from sqlalchemy.orm import Session

from ..models import Pond
from .base import BaseRepository


class PondRepository(BaseRepository[Pond]):
    def __init__(self, db: Session):
        super().__init__(Pond, db)

    def get_by_name(self, name: str) -> Optional[Pond]:
        return self.db.query(Pond).filter(Pond.name == name).first()

    def exists_by_name(self, name: str) -> bool:
        return self.db.query(Pond.id).filter(Pond.name == name).first() is not None
