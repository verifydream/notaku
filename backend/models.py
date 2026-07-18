"""SQLAlchemy database models for NotaKu.

This module contains the SQLAlchemy declarative base models representing
the core entities: Users, MenuItems, Transactions, and TransactionItems.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def utcnow():
    """Generates the current UTC datetime.

    Returns:
        datetime: A timezone-aware datetime object representing the current UTC time.
    """
    return datetime.now(timezone.utc)


def gen_uuid():
    """Generates a UUID string.

    Returns:
        str: A string representation of a randomly generated UUID4.
    """
    return str(uuid.uuid4())


class User(Base):
    """Represents a warung owner or user in the system.

    Attributes:
        id (str): Primary key, UUID string.
        phone (str): The user's WhatsApp phone number (unique).
        name (str | None): The user's name.
        warung_name (str | None): The name of the user's shop/warung.
        created_at (datetime): Timestamp when the user was created.
        menu_items (list[MenuItem]): Relationship to the user's menu items.
        transactions (list[Transaction]): Relationship to the user's transactions.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100))
    warung_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class MenuItem(Base):
    """Represents an item available for sale by a specific user.

    Attributes:
        id (str): Primary key, UUID string.
        user_id (str): Foreign key linking to the User.
        name (str): Name of the menu item.
        price (int): Price of the item in Rupiah.
        aliases (list[str] | None): List of alternative names for AI matching.
        active (bool): Whether the item is currently active/available.
        created_at (datetime): Timestamp when the item was created.
        user (User): Relationship back to the owner User.
        transaction_items (list[TransactionItem]): Relationship to transaction items.
    """
    __tablename__ = "menu_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)  # Rupiah
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="menu_items")
    transaction_items: Mapped[list["TransactionItem"]] = relationship(back_populates="menu_item")


class Transaction(Base):
    """Represents a transaction (sale or expense) made by a user.

    Attributes:
        id (str): Primary key, UUID string.
        user_id (str): Foreign key linking to the User.
        customer_phone (str | None): Phone number of the customer, if applicable.
        total (int): Total amount of the transaction in Rupiah.
        type (str): Type of transaction, typically "sale" or "expense".
        note (str | None): Optional note regarding the transaction.
        created_at (datetime): Timestamp when the transaction was recorded.
        user (User): Relationship back to the owner User.
        items (list[TransactionItem]): Relationship to the items within this transaction.
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    customer_phone: Mapped[str | None] = mapped_column(String(20))
    total: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(10), default="sale")  # sale | expense
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="transactions")
    items: Mapped[list["TransactionItem"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    """Represents an individual line item within a Transaction.

    Attributes:
        id (str): Primary key, UUID string.
        transaction_id (str): Foreign key linking to the Transaction.
        menu_item_id (str): Foreign key linking to the MenuItem.
        quantity (int): Number of items purchased.
        unit_price (int): Price per unit at the time of transaction.
        subtotal (int): Total cost for this line item (quantity * unit_price).
        transaction (Transaction): Relationship back to the parent Transaction.
        menu_item (MenuItem): Relationship back to the associated MenuItem.
    """
    __tablename__ = "transaction_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id"))
    menu_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[int] = mapped_column(Integer)

    transaction: Mapped["Transaction"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="transaction_items")
