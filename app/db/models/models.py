import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "toolsprice_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    budgets = relationship("Budget", back_populates="owner")
    products = relationship("Product", back_populates="user")


class Product(Base):
    __tablename__ = "toolsprice_products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    nombre = Column(String(255), nullable=False)
    categoria = Column(String(255))
    precio = Column(Float, nullable=False)
    moneda = Column(String(10), default="MXN")
    unidad_medida = Column(String(100))
    marca = Column(String(100))
    caracteristicas = Column(Text)
    url_producto = Column(String(1000))
    imagen_url = Column(String(1000))
    tienda = Column(String(255))
    disponibilidad = Column(Boolean, default=True)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="products")


class Budget(Base):
    __tablename__ = "toolsprice_budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    budget_type = Column(String(50), default="construccion")
    subtotal = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    total = Column(Float, default=0)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="budgets")
    items = relationship("BudgetItem", back_populates="budget")


class BudgetItem(Base):
    __tablename__ = "toolsprice_budget_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = Column(String(36), ForeignKey("budgets.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"))
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="items")
    product = relationship("Product")


class ScrapingLog(Base):
    __tablename__ = "toolsprice_scraping_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tienda = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)