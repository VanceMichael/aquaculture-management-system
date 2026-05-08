from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from ..models import HarvestSale
from ..schemas import HarvestSaleCreate, HarvestSaleUpdate, HarvestSaleResponse
from ..repositories import HarvestRepository, BatchRepository


class HarvestService:
    def __init__(self, db: Session):
        self.db = db
        self.harvest_repo = HarvestRepository(db)
        self.batch_repo = BatchRepository(db)

    def create_harvest_sale(self, sale_in: Dict[str, Any]) -> HarvestSale:
        if not self.batch_repo.get_by_id(sale_in.get('batch_id')):
            raise ValueError("批次不存在")

        if sale_in.get('total_amount') is None:
            sale_in['total_amount'] = sale_in.get('weight', 0) * sale_in.get('unit_price', 0)

        return self.harvest_repo.create(sale_in)

    def get_harvest_sales(
        self,
        skip: int = 0,
        limit: int = 100,
        batch_id: Optional[int] = None,
    ) -> List[HarvestSale]:
        filters = {}
        if batch_id is not None:
            filters['batch_id'] = batch_id
        return self.harvest_repo.get_all(skip=skip, limit=limit, filters=filters)

    def get_harvest_sale(self, sale_id: int) -> Optional[HarvestSale]:
        return self.harvest_repo.get_by_id(sale_id)

    def update_harvest_sale(
        self,
        sale_id: int,
        update_data: Dict[str, Any],
    ) -> HarvestSale:
        db_sale = self.harvest_repo.get_by_id(sale_id)
        if not db_sale:
            raise ValueError("出塘销售记录不存在")

        if 'weight' in update_data or 'unit_price' in update_data:
            weight = update_data.get('weight', db_sale.weight)
            unit_price = update_data.get('unit_price', db_sale.unit_price)
            update_data['total_amount'] = weight * unit_price

        return self.harvest_repo.update(db_sale, update_data)

    def delete_harvest_sale(self, sale_id: int) -> None:
        db_sale = self.harvest_repo.get_by_id(sale_id)
        if not db_sale:
            raise ValueError("出塘销售记录不存在")
        self.harvest_repo.delete(db_sale)
