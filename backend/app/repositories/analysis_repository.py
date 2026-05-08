from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    Pond,
    StockingRecord,
    FeedingRecord,
    CostRecord,
    HarvestSale,
    WaterQualityRecord,
    MedicationRecord,
)


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_pond_by_id(self, pond_id: int) -> Optional[Pond]:
        return self.db.query(Pond).filter(Pond.id == pond_id).first()

    def sum_stocking_quantity(self, batch_id: int) -> int:
        result = self.db.query(func.sum(StockingRecord.quantity)).filter(
            StockingRecord.batch_id == batch_id
        ).scalar()
        return result or 0

    def sum_harvest_weight(self, batch_id: int) -> float:
        result = self.db.query(func.sum(HarvestSale.weight)).filter(
            HarvestSale.batch_id == batch_id
        ).scalar()
        return result or 0.0

    def sum_feed_quantity(self, batch_id: int) -> float:
        result = self.db.query(func.sum(FeedingRecord.feed_quantity)).filter(
            FeedingRecord.batch_id == batch_id
        ).scalar()
        return result or 0.0

    def sum_cost_amount(self, batch_id: int) -> float:
        result = self.db.query(func.sum(CostRecord.amount)).filter(
            CostRecord.batch_id == batch_id
        ).scalar()
        return result or 0.0

    def sum_revenue(self, batch_id: int) -> float:
        result = self.db.query(func.sum(HarvestSale.total_amount)).filter(
            HarvestSale.batch_id == batch_id
        ).scalar()
        return result or 0.0

    def get_cost_breakdown(self, batch_id: int) -> Dict[str, float]:
        costs = self.db.query(
            CostRecord.cost_type,
            func.sum(CostRecord.amount).label('total')
        ).filter(
            CostRecord.batch_id == batch_id
        ).group_by(CostRecord.cost_type).all()
        return {c.cost_type: c.total for c in costs}

    def get_feeding_summary(self, batch_id: int) -> List[Tuple[str, float, int]]:
        return self.db.query(
            FeedingRecord.feed_type,
            func.sum(FeedingRecord.feed_quantity).label('total_quantity'),
            func.count(FeedingRecord.id).label('feeding_count')
        ).filter(
            FeedingRecord.batch_id == batch_id
        ).group_by(FeedingRecord.feed_type).all()

    def get_stocking_records(self, batch_id: int) -> List[StockingRecord]:
        return self.db.query(StockingRecord).filter(
            StockingRecord.batch_id == batch_id
        ).all()

    def get_feeding_records(self, batch_id: int) -> List[FeedingRecord]:
        return self.db.query(FeedingRecord).filter(
            FeedingRecord.batch_id == batch_id
        ).all()

    def get_water_quality_records(self, batch_id: int) -> List[WaterQualityRecord]:
        return self.db.query(WaterQualityRecord).filter(
            WaterQualityRecord.batch_id == batch_id
        ).all()

    def get_medication_records(self, batch_id: int) -> List[MedicationRecord]:
        return self.db.query(MedicationRecord).filter(
            MedicationRecord.batch_id == batch_id
        ).all()

    def get_cost_records(self, batch_id: int) -> List[CostRecord]:
        return self.db.query(CostRecord).filter(
            CostRecord.batch_id == batch_id
        ).all()

    def get_harvest_sales(self, batch_id: int) -> List[HarvestSale]:
        return self.db.query(HarvestSale).filter(
            HarvestSale.batch_id == batch_id
        ).all()
