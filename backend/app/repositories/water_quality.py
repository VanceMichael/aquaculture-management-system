from typing import Optional, List
from sqlalchemy.orm import Session
from ..models import WaterQualityRecord, Batch
from .base import BaseRepository


class WaterQualityRepository(BaseRepository[WaterQualityRecord]):
    def __init__(self, db: Session) -> None:
        super().__init__(WaterQualityRecord, db)

    def get_by_batch_id(
        self, batch_id: int, skip: int = 0, limit: int = 100
    ) -> List[WaterQualityRecord]:
        return (
            self.db.query(WaterQualityRecord)
            .filter(WaterQualityRecord.batch_id == batch_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_list_with_filter(
        self, skip: int = 0, limit: int = 100, batch_id: Optional[int] = None
    ) -> List[WaterQualityRecord]:
        query = self.db.query(WaterQualityRecord)
        if batch_id is not None:
            query = query.filter(WaterQualityRecord.batch_id == batch_id)
        return query.offset(skip).limit(limit).all()

    def batch_exists(self, batch_id: int) -> bool:
        return self.db.query(Batch).filter(Batch.id == batch_id).first() is not None
