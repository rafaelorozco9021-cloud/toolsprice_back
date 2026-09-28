from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.products import router as products_router
from app.api.routes.budgets import router as budgets_router
from app.api.routes.labor import router as labor_router
from app.db.session import init_db

app = FastAPI(
    title="ToolsPrice API",
    description="API para presupuestos de construcción - Homecenter",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(budgets_router, prefix="/api")
app.include_router(labor_router, prefix="/api")


@app.on_event("startup")
async def startup():
    try:
        await init_db()
    except Exception as e:
        print(f"DB init warning: {e}")


@app.get("/")
def root():
    return {"message": "ToolsPrice API"}


@app.get("/health")
def health():
    return {"status": "ok"}