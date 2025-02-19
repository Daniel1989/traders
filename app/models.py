from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from decimal import Decimal
from sqlalchemy import Column, DECIMAL

class Goods(SQLModel, table=True):
    """Futures goods model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class GoodsPriceInSecond(SQLModel, table=True):
    """Futures price record model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(index=True)  # Symbol identifier (e.g., ag2504)
    goods: int = Field(foreign_key="goods.id")  # Reference to Goods table
    price_time: str
    
    # Use SQLAlchemy Column for decimal fields
    current_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    price_diff: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    price_diff_percent: Decimal = Field(sa_column=Column(DECIMAL(10, 4)))
    close_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    open_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    high_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    low_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    compute_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    prev_compute_price: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    
    have_vol: int
    deal_vol: int
    buy_price_oncall: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    sell_price_oncall: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    buy_vol: int
    sell_vol: int
    created_at: datetime = Field(default_factory=datetime.now) 