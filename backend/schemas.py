"""Pydantic schemas for the NotaKu API.

This module defines the data validation and serialization models
used for API requests and responses.
"""

from datetime import datetime
from pydantic import BaseModel


# --- Menu ---
class MenuItemCreate(BaseModel):
    """Schema for creating a new menu item.

    Attributes:
        name (str): The name of the menu item.
        price (int): The price in Rupiah.
        aliases (list[str]): Optional list of alternative names for AI matching.
    """
    name: str
    price: int
    aliases: list[str] = []


class MenuItemOut(BaseModel):
    """Schema for serializing a menu item in responses.

    Attributes:
        id (str): The unique ID of the item.
        name (str): The name of the item.
        price (int): The price in Rupiah.
        aliases (list[str] | None): The alternative names for the item.
        active (bool): Whether the item is active.
    """
    id: str
    name: str
    price: int
    aliases: list[str] | None = None
    active: bool

    model_config = {"from_attributes": True}


# --- Transaction ---
class TransactionItemOut(BaseModel):
    """Schema for serializing a transaction line item.

    Attributes:
        id (str): The unique ID of the transaction item.
        menu_item_name (str): The name of the matched menu item.
        quantity (int): Number of units.
        unit_price (int): Price per unit.
        subtotal (int): Total for this line item.
    """
    id: str
    menu_item_name: str
    quantity: int
    unit_price: int
    subtotal: int

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    """Schema for serializing a transaction.

    Attributes:
        id (str): The unique ID of the transaction.
        total (int): The total amount for the transaction.
        type (str): Transaction type ("sale" or "expense").
        note (str | None): Optional note.
        customer_phone (str | None): Optional customer phone number.
        items (list[TransactionItemOut]): List of items in the transaction.
        created_at (datetime): The creation timestamp.
    """
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
    """Schema for serializing user information.

    Attributes:
        id (str): The unique ID of the user.
        phone (str): The WhatsApp phone number of the user.
        name (str | None): The user's name.
        warung_name (str | None): The user's shop name.
        created_at (datetime): The creation timestamp.
    """
    id: str
    phone: str
    name: str | None = None
    warung_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Dashboard summary ---
class DailySummary(BaseModel):
    """Schema for a daily dashboard summary.

    Attributes:
        date (str): The date string for the summary (e.g., 'YYYY-MM-DD').
        total_sales (int): The sum of all sales on this date.
        total_expenses (int): The sum of all expenses on this date.
        profit (int): The net profit (sales - expenses).
        transaction_count (int): The number of transactions.
        top_items (list[dict]): A list of the most sold items.
    """
    date: str
    total_sales: int
    total_expenses: int
    profit: int
    transaction_count: int
    top_items: list[dict]
