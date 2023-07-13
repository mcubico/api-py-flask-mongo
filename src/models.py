from enum import Enum
from typing import Optional, TypedDict

from pydantic import BaseModel, Field


class LevelRiskEnum(str, Enum):
    HIGH = 'high'
    MIDDLE = 'middle'
    LOW = 'low'


class FeatureModel(BaseModel):
    vulnerability: LevelRiskEnum
    probability: LevelRiskEnum
    impact: LevelRiskEnum
    thread: LevelRiskEnum


class RiskModel(BaseModel):
    risk: str
    description: str
    active: bool
    features: FeatureModel


class RoleEnum(str, Enum):
    ADMIN = 'admin'
    GUEST = 'guest'


class AccountModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    role: RoleEnum = RoleEnum.GUEST


class LoginModel(BaseModel):
    username: str
    password: str

    def to_json(self):
        return {
            'username': self.username,
            'password': self.password
        }


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
    order: Optional[OrderPaginationEnum] = OrderPaginationEnum.ASCENDING


class ApiHttpResponseModel(TypedDict):
    status: str
    message: Optional[str]
    data: Optional[object]
    error: Optional[bool]
