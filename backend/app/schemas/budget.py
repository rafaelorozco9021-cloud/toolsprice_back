from pydantic import BaseModel
from typing import List, Optional


class BudgetItem(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    quantity: int = 1
    unit_price: float
    total_price: float


from typing import Literal

BudgetType = Literal["construccion", "soldadura", "pintura", "plomeria", "herramientas", "mano_obra"]


class BudgetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    items: List[BudgetItem]
    tax_rate: float = 0.16
    budget_type: BudgetType = "construccion"


class BudgetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    budget_type: str = "construccion"
    subtotal: float
    tax_amount: float
    total: float
    status: str
    created_at: str
