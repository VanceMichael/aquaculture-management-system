from typing import Optional, List
from sqlalchemy.orm import Session

from ..models import Batch
from .base import BaseRepository


class BatchRepository(BaseRepository[Batch]):
    def __init__(self, db: Session):
        super().__init__(Batch, db)

    def get_by_batch_number(self, batch_number: str) -> Optional[Batch]:
        return self.db.query(Batch).filter(Batch.batch_number == batch_number).first()

    def exists_by_batch_number(self, batch_number: str) -> bool:
        return self.db.query(Batch.id).filter(Batch.batch_number == batch_number).first() is not None
