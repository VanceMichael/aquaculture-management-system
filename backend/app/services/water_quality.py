from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import WaterQualityRecord
from ..schemas import WaterQualityRecordCreate, WaterQualityRecordUpdate
from ..repositories.water_quality import WaterQualityRepository


class WaterQualityService:
    def __init__(self, db: Session) -> None:
        self.repo: WaterQualityRepository = WaterQualityRepository(db)

    def create_record(self, data: WaterQualityRecordCreate) -> WaterQualityRecord:
        if not self.repo.batch_exists(data.batch_id):
            raise HTTPException(status_code=404, detail="批次不存在")
        new_record = WaterQualityRecord(**data.dict())
        return self.repo.create(new_record)

    def get_records(
        self, skip: int = 0, limit: int = 100, batch_id: Optional[int] = None
    ) -> List[WaterQualityRecord]:
        return self.repo.get_list_with_filter(skip=skip, limit=limit, batch_id=batch_id)

    def get_record(self, record_id: int) -> WaterQualityRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="水质监测记录不存在")
        return record

    def update_record(
        self, record_id: int, data: WaterQualityRecordUpdate
    ) -> WaterQualityRecord:
        db_record = self.repo.get_by_id(record_id)
        if not db_record:
            raise HTTPException(status_code=404, detail="水质监测记录不存在")
        update_data = data.dict(exclude_unset=True)
        return self.repo.update(db_record, update_data)

    def delete_record(self, record_id: int) -> dict:
        db_record = self.repo.get_by_id(record_id)
        if not db_record:
            raise HTTPException(status_code=404, detail="水质监测记录不存在")
        self.repo.delete(db_record)
        return {"message": "水质监测记录删除成功"}
