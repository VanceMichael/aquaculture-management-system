from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from ..models import HarvestSale
from .base import BaseRepository


class HarvestRepository(BaseRepository[HarvestSale]):
    def __init__(self, db: Session):
        super().__init__(HarvestSale, db)
