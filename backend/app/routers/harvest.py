from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import HarvestSaleCreate, HarvestSaleUpdate, HarvestSaleResponse
from ..services import HarvestService

router = APIRouter(
    prefix="/api/harvest-sales",
    tags=["出塘销售"],
)


def get_harvest_service(db: Session = Depends(get_db)) -> HarvestService:
    return HarvestService(db)


@router.post("/", response_model=HarvestSaleResponse)
def create_harvest_sale(
    sale: HarvestSaleCreate,
    service: HarvestService = Depends(get_harvest_service),
) -> HarvestSaleResponse:
    try:
        return service.create_harvest_sale(sale.dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=List[HarvestSaleResponse])
def get_harvest_sales(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    service: HarvestService = Depends(get_harvest_service),
) -> List[HarvestSaleResponse]:
    return service.get_harvest_sales(skip=skip, limit=limit, batch_id=batch_id)


@router.get("/{sale_id}/", response_model=HarvestSaleResponse)
def get_harvest_sale(
    sale_id: int,
    service: HarvestService = Depends(get_harvest_service),
) -> HarvestSaleResponse:
    sale = service.get_harvest_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="出塘销售记录不存在")
    return sale


@router.put("/{sale_id}/", response_model=HarvestSaleResponse)
def update_harvest_sale(
    sale_id: int,
    sale: HarvestSaleUpdate,
    service: HarvestService = Depends(get_harvest_service),
) -> HarvestSaleResponse:
    try:
        return service.update_harvest_sale(sale_id, sale.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{sale_id}/")
def delete_harvest_sale(
    sale_id: int,
    service: HarvestService = Depends(get_harvest_service),
) -> dict:
    try:
        service.delete_harvest_sale(sale_id)
        return {"message": "出塘销售记录删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
