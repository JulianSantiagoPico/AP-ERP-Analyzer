# Copyright 2025 Anti-Patrones
# This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.
# http://creativecommons.org/licenses/by-sa/4.0/

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import financial_kpis, sales_analysis, accounts, expenses, ml_predictions

def create_app(config_name='development'):
    """Crea y configura la aplicación FastAPI"""
    
    app = FastAPI(
        title="AP-ERP-Analyzer-BE",
        description="API para análisis de datos ERP y visualización de KPIs",
        version="1.0.0"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar orígenes permitidos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.include_router(financial_kpis.router, prefix="/api/kpis/financial", tags=["Financial KPIs"])
    app.include_router(sales_analysis.router, prefix="/api/kpis/sales", tags=["Sales Analysis"])
    app.include_router(accounts.router, prefix="/api/kpis/accounts", tags=["Accounts Receivable/Payable"])
    app.include_router(expenses.router, prefix="/api/kpis/expenses", tags=["Expenses Analysis"])
    app.include_router(ml_predictions.router, prefix="/api/ml", tags=["ML Predictions"])
    
    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Welcome to the ERP Analyzer API"}
    
    return app