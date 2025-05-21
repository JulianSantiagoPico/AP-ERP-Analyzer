from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from app.routers import financial_kpis, sales_analysis, accounts, expenses, ml_predictions

# Create FastAPI instance
app = FastAPI(
    title="ERP Analyzer API",
    description="API for analyzing ERP data and providing business insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(financial_kpis.router, prefix="/api/kpis/financial", tags=["Financial KPIs"])
app.include_router(sales_analysis.router, prefix="/api/kpis/sales", tags=["Sales Analysis"])
app.include_router(accounts.router, prefix="/api/kpis/accounts", tags=["Accounts Receivable/Payable"])
app.include_router(expenses.router, prefix="/api/kpis/expenses", tags=["Expenses Analysis"])
app.include_router(ml_predictions.router, prefix="/api/ml", tags=["ML Predictions"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the ERP Analyzer API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
