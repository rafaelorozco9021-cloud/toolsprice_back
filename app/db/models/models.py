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
    # Empresa (opcional): si tiene, el PDF muestra la empresa en el encabezado
    # y al dueño/representante en la firma; si no, se usa ToolsPrice
    has_company = Column(Boolean, default=False)
    company_name = Column(String(255))
    owner_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    budgets = relationship("Budget", back_populates="owner")
    products = relationship("Product", back_populates="user")


class Product(Base):
    __tablename__ = "toolsprice_products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("toolsprice_users.id"))
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


class CatalogProduct(Base):
    """Catálogo pre-scrapeado de Homecenter.

    Se llena con el crawl nocturno (00:00) y sirve las búsquedas desde DB
    con tiempos de respuesta < 200ms. sku es la clave de upsert.
    Separado de toolsprice_products (mock/user) para no romper flujos existentes.
    """
    __tablename__ = "toolsprice_catalog_products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(500), nullable=False)
    marca = Column(String(150))
    categoria = Column(String(255), index=True)
    categoria_url = Column(String(1000))
    precio = Column(Float, nullable=False, default=0, index=True)
    moneda = Column(String(10), default="COP")
    unidad_medida = Column(String(100))
    imagen_url = Column(String(1000))
    url_producto = Column(String(1000), index=True)
    disponibilidad = Column(Boolean, default=True)
    caracteristicas = Column(Text)
    fuente = Column(String(50), default="homecenter")
    last_scraped_at = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "toolsprice_budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("toolsprice_users.id"), nullable=False)
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
    budget_id = Column(String(36), ForeignKey("toolsprice_budgets.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("toolsprice_products.id"))
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    # 'materiales' | 'mano_obra' — para el PDF unificado de 2 secciones
    seccion = Column(String(20), default="materiales")
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


class SearchLog(Base):
    """Una fila por búsqueda hecha desde web o mobile. Sirve para 'lo más buscado' del landing."""
    __tablename__ = "toolsprice_search_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(120), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("toolsprice_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)