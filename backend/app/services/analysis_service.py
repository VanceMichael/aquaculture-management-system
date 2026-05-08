from typing import Optional, Dict, Any
from datetime import date

from sqlalchemy.orm import Session

from ..models import Batch
from ..schemas import (
    CultureCycleAnalysis,
    BatchTraceability,
    BatchInfo,
    PondInfo,
)
from ..repositories import (
    BatchRepository,
    AnalysisRepository,
)


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.batch_repo = BatchRepository(db)
        self.analysis_repo = AnalysisRepository(db)

    def analyze_cycle(self, batch_id: int) -> CultureCycleAnalysis:
        batch = self.batch_repo.get_by_id(batch_id)
        if not batch:
            raise ValueError("批次不存在")

        pond = self.analysis_repo.get_pond_by_id(batch.pond_id)

        initial_quantity = self.analysis_repo.sum_stocking_quantity(batch.id)
        harvest_weight = self.analysis_repo.sum_harvest_weight(batch.id)
        feed_total = self.analysis_repo.sum_feed_quantity(batch.id)
        total_cost = self.analysis_repo.sum_cost_amount(batch.id)
        total_revenue = self.analysis_repo.sum_revenue(batch.id)

        harvest_date = batch.actual_harvest_date
        days_cultured = self._calculate_days_cultured(harvest_date, batch.stocking_date)
        survival_rate = self._calculate_survival_rate(initial_quantity, harvest_weight)
        feed_conversion_ratio = self._calculate_fcr(harvest_weight, feed_total)
        yield_per_mu = self._calculate_yield_per_mu(pond.area if pond else 0, harvest_weight)
        profit = total_revenue - total_cost

        cost_summary = self._build_cost_summary(batch.id, total_cost)
        feeding_summary = self._build_feeding_summary(batch.id, feed_total, days_cultured)

        return CultureCycleAnalysis(
            batch_number=batch.batch_number,
            pond_name=pond.name if pond else "未知",
            species=batch.species,
            stocking_date=batch.stocking_date,
            harvest_date=harvest_date,
            days_cultured=days_cultured,
            initial_quantity=initial_quantity,
            harvest_weight=harvest_weight,
            survival_rate=round(survival_rate, 2),
            feed_total=feed_total,
            feed_conversion_ratio=round(feed_conversion_ratio, 2),
            area=pond.area if pond else 0,
            yield_per_mu=round(yield_per_mu, 2),
            total_cost=total_cost,
            total_revenue=total_revenue,
            profit=profit,
            cost_summary=cost_summary,
            feeding_summary=feeding_summary,
        )

    def batch_traceability(self, batch_id: int) -> BatchTraceability:
        batch = self.batch_repo.get_by_id(batch_id)
        if not batch:
            raise ValueError("批次不存在")

        pond = self.analysis_repo.get_pond_by_id(batch.pond_id)
        stocking_records = self.analysis_repo.get_stocking_records(batch.id)
        feeding_records = self.analysis_repo.get_feeding_records(batch.id)
        water_quality_records = self.analysis_repo.get_water_quality_records(batch.id)
        medication_records = self.analysis_repo.get_medication_records(batch.id)
        cost_records = self.analysis_repo.get_cost_records(batch.id)
        harvest_sales = self.analysis_repo.get_harvest_sales(batch.id)

        return BatchTraceability(
            batch=BatchInfo(
                batch_number=batch.batch_number,
                species=batch.species,
                stocking_date=batch.stocking_date,
                harvest_date=batch.actual_harvest_date,
                status=batch.status,
                pond_id=batch.pond_id,
            ),
            pond_info=PondInfo(
                name=pond.name if pond else None,
                area=pond.area if pond else None,
                water_depth=pond.water_depth if pond else None,
            ),
            stocking_records=[
                {
                    "species": r.species,
                    "quantity": r.quantity,
                    "source": r.source,
                    "batch_number": r.batch_number,
                    "stocking_date": r.created_at.date() if hasattr(r, 'created_at') else None,
                }
                for r in stocking_records
            ],
            feeding_records=[
                {
                    "feeding_date": r.feeding_date,
                    "feed_type": r.feed_type,
                    "quantity": r.feed_quantity,
                    "unit": "kg",
                }
                for r in feeding_records
            ],
            water_quality_records=[
                {
                    "record_date": r.record_date,
                    "water_temperature": r.water_temperature,
                    "ph_value": r.ph_value,
                    "dissolved_oxygen": r.dissolved_oxygen,
                }
                for r in water_quality_records
            ],
            medication_records=[
                {
                    "medication_date": r.medication_date,
                    "medication_name": r.drug_name,
                    "dosage": r.dosage,
                    "unit": r.dosage_unit,
                }
                for r in medication_records
            ],
            cost_records=[
                {
                    "cost_date": r.cost_date,
                    "cost_type": r.cost_type,
                    "amount": r.amount,
                    "description": r.description,
                }
                for r in cost_records
            ],
            harvest_sales=[
                {
                    "sale_date": r.sale_date,
                    "weight": r.weight,
                    "unit_price": r.unit_price,
                    "total_amount": r.total_amount,
                    "buyer": r.buyer,
                }
                for r in harvest_sales
            ],
        )

    def trace_by_batch_number(self, batch_number: str) -> BatchTraceability:
        batch = self.batch_repo.get_by_batch_number(batch_number)
        if not batch:
            raise ValueError(f"批次号 {batch_number} 不存在")
        return self.batch_traceability(batch.id)

    @staticmethod
    def _calculate_days_cultured(harvest_date: Optional[date], stocking_date: date) -> Optional[int]:
        if harvest_date:
            return (harvest_date - stocking_date).days
        return None

    @staticmethod
    def _calculate_survival_rate(initial_quantity: int, harvest_weight: float) -> float:
        if initial_quantity > 0 and harvest_weight > 0:
            avg_weight_per_fish = 0.5
            estimated_survival = harvest_weight / avg_weight_per_fish
            return (estimated_survival / initial_quantity) * 100
        return 0.0

    @staticmethod
    def _calculate_fcr(harvest_weight: float, feed_total: float) -> float:
        if harvest_weight > 0 and feed_total > 0:
            return feed_total / harvest_weight
        return 0.0

    @staticmethod
    def _calculate_yield_per_mu(pond_area: float, harvest_weight: float) -> float:
        if pond_area > 0:
            return harvest_weight / pond_area
        return 0.0

    def _build_cost_summary(self, batch_id: int, total_cost: float) -> Dict[str, float]:
        cost_breakdown = self.analysis_repo.get_cost_breakdown(batch_id)

        known_types = ['feed', 'medicine', 'labor', 'electricity']
        other_cost = sum(
            amount for cost_type, amount in cost_breakdown.items()
            if cost_type not in known_types
        )

        return {
            "feed_cost": cost_breakdown.get('feed', 0),
            "medicine_cost": cost_breakdown.get('medicine', 0),
            "labor_cost": cost_breakdown.get('labor', 0),
            "electricity_cost": cost_breakdown.get('electricity', 0),
            "other_cost": other_cost,
            "total_cost": total_cost,
        }

    def _build_feeding_summary(
        self,
        batch_id: int,
        total_feed_weight: float,
        days_cultured: Optional[int],
    ) -> Dict[str, float]:
        feeding_summary_list = self.analysis_repo.get_feeding_summary(batch_id)
        feeding_count = sum(f.feeding_count for f in feeding_summary_list)

        avg_daily_feed = 0.0
        if days_cultured and days_cultured > 0:
            avg_daily_feed = total_feed_weight / days_cultured

        return {
            "total_feed_weight": total_feed_weight,
            "feeding_count": feeding_count,
            "avg_daily_feed": avg_daily_feed,
        }
