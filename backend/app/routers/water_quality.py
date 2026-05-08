from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import WaterQualityRecordCreate, WaterQualityRecordUpdate, WaterQualityRecordResponse
from ..services.water_quality import WaterQualityService

router = APIRouter(
    prefix="/api/water-quality-records",
    tags=["水质监测"]
)


def _get_service(db: Session = Depends(get_db)) -> WaterQualityService:
    return WaterQualityService(db)


@router.post("/", response_model=WaterQualityRecordResponse)
def create_water_quality_record(
    record: WaterQualityRecordCreate,
    service: WaterQualityService = Depends(_get_service),
):
    return service.create_record(record)


@router.get("/", response_model=List[WaterQualityRecordResponse])
def get_water_quality_records(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    service: WaterQualityService = Depends(_get_service),
):
    return service.get_records(skip=skip, limit=limit, batch_id=batch_id)


@router.get("/{record_id}/", response_model=WaterQualityRecordResponse)
def get_water_quality_record(
    record_id: int,
    service: WaterQualityService = Depends(_get_service),
):
    return service.get_record(record_id)


@router.put("/{record_id}/", response_model=WaterQualityRecordResponse)
def update_water_quality_record(
    record_id: int,
    record: WaterQualityRecordUpdate,
    service: WaterQualityService = Depends(_get_service),
):
    return service.update_record(record_id, record)


@router.delete("/{record_id}/")
def delete_water_quality_record(
    record_id: int,
    service: WaterQualityService = Depends(_get_service),
):
    return service.delete_record(record_id)
