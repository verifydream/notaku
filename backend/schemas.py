"""Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel


# --- Menu ---
class MenuItemCreate(BaseModel):
    name: str
    price: int
    aliases: list[str] = []


class MenuItemOut(BaseModel):
    id: str
    name: str
    price: int
    aliases: list[str] | None = None
    active: bool

    model_config = {"from_attributes": True}


# --- Transaction ---
class TransactionItemOut(BaseModel):
    id: str
    menu_item_name: str
    quantity: int
    unit_price: int
    subtotal: int

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    id: str
    total: int
    type: str
    note: str | None = None
    customer_phone: str | None = None
    items: list[TransactionItemOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# --- User ---
class UserOut(BaseModel):
    id: str
    phone: str
    name: str | None = None
    warung_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Dashboard summary ---
class DailySummary(BaseModel):
    date: str
    total_sales: int
    total_expenses: int
    profit: int
    transaction_count: int
    top_items: list[dict]
