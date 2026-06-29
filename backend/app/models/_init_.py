import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Numeric, Enum, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# --- Базовый класс и Enum ---
class Base(DeclarativeBase):
    pass

class UserType(PyEnum):
    B2C = "b2c"
    B2B = "b2b"

class OrderStatus(PyEnum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# --- Модели ---

class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bot_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    theme_config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    users: Mapped[list["User"]] = relationship(back_populates="company")
    products: Mapped[list["Product"]] = relationship(back_populates="company")
    pricing_tiers: Mapped[list["PricingTier"]] = relationship(back_populates="company")


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), nullable=False)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=True)
    
    fio: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    company: Mapped["Company"] = relationship(back_populates="users")
    b2b_details: Mapped["B2BDetails"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class B2BDetails(Base):
    __tablename__ = "b2b_details"
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    pricing_tier_id: Mapped[str] = mapped_column(String(36), ForeignKey("pricing_tiers.id"), nullable=True)
    payment_terms: Mapped[str] = mapped_column(Text, nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="b2b_details")
    pricing_tier: Mapped["PricingTier"] = relationship(back_populates="b2b_users")


class PricingTier(Base):
    __tablename__ = "pricing_tiers"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)

    # Связи
    company: Mapped["Company"] = relationship(back_populates="pricing_tiers")
    b2b_users: Mapped[list["B2BDetails"]] = relationship(back_populates="pricing_tier")
    b2b_prices: Mapped[list["B2BPrice"]] = relationship(back_populates="pricing_tier")


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    company: Mapped["Company"] = relationship(back_populates="products")
    b2b_prices: Mapped[list["B2BPrice"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class B2BPrice(Base):
    __tablename__ = "b2b_prices"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    pricing_tier_id: Mapped[str] = mapped_column(String(36), ForeignKey("pricing_tiers.id"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Связи
    product: Mapped["Product"] = relationship(back_populates="b2b_prices")
    pricing_tier: Mapped["PricingTier"] = relationship(back_populates="b2b_prices")


class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Связи
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")