from enum import Enum
from typing import List, Optional

import pymongo
from pydantic import BaseModel, Field


class LevelRiskEnum(str, Enum):
    HIGH = 'high'
    MIDDLE = 'middle'
    LOW = 'low'


class FeatureModel(BaseModel):
    id: int = Field(None, alias="_id")
    vulnerability: LevelRiskEnum
    probability: LevelRiskEnum
    impact: LevelRiskEnum
    thread: LevelRiskEnum


class RiskModel(BaseModel):
    id: int = Field(None, alias="_id")
    risk: str
    description: str
    active: bool
    features: FeatureModel


class LoginModel(BaseModel):
    username: str
    password: str


class OrderPaginationEnum(str, Enum):
    ASCENDING = 'asc'
    DESCENDING = 'desc'


class ColumnOrderFetchRiskEnum(str, Enum):
    VULNERABILITY = 'vulnerability'
    PROBABILITY = 'probability'
    IMPACT = 'impact'
    THREAT = 'threat'


class PaginationModel(BaseModel):
    query: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10
    order_by: Optional[ColumnOrderFetchRiskEnum] = None
    order: Optional[OrderPaginationEnum] = OrderPaginationEnum.ASCENDING,
