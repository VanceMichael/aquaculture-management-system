from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas import CultureCycleAnalysis, BatchTraceability
from ..services import AnalysisService

router = APIRouter(
    prefix="/api/analysis",
    tags=["养殖周期分析"],
)


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)


@router.get("/cycle/{batch_id}/", response_model=CultureCycleAnalysis)
def analyze_cycle(
    batch_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> CultureCycleAnalysis:
    try:
        return service.analyze_cycle(batch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/traceability/{batch_id}/", response_model=BatchTraceability)
def batch_traceability(
    batch_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> BatchTraceability:
    try:
        return service.batch_traceability(batch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trace-by-number/{batch_number}/", response_model=BatchTraceability)
def trace_by_batch_number(
    batch_number: str,
    service: AnalysisService = Depends(get_analysis_service),
) -> BatchTraceability:
    try:
        return service.trace_by_batch_number(batch_number)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
