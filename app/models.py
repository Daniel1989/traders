from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from decimal import Decimal
from sqlalchemy import Column, DECIMAL, PrimaryKeyConstraint

class Goods(SQLModel, table=True):
    """Futures goods model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    title: Optional[str] = None  # Added title field with default None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class GoodsPriceInSecond(SQLModel, table=True):
    """Futures price record model"""
    __table_args__ = (
        PrimaryKeyConstraint('id', 'created_at'),
    )
    
    id: int = Field()  # Part of composite primary key
    uid: str = Field(index=True)  # Symbol identifier (e.g., ag2504)
    goods: str  # Changed from int to str, removed foreign key
    price_time: str
    created_at: datetime = Field(default_factory=datetime.now)  # Part of composite primary key
    
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