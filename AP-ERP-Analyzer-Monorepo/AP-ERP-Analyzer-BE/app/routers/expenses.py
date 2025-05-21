from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.financial_kpis_service import financial_kpis_service

router = APIRouter()

@router.get("/")
async def get_expenses_analysis(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    top_n: int = Query(10, description="Number of top suppliers to return")
):
    """
    Get expenses analysis by supplier
    """
    try:
        result = financial_kpis_service.analyze_expenses_by_supplier(year=year, month=month, top_n=top_n)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing expenses: {str(e)}")

@router.get("/by-period")
async def get_expenses_by_period():
    """
    Get expenses data grouped by period for trend analysis
    """
    try:
        # Get all expenses data
        result = financial_kpis_service.analyze_expenses_by_supplier()
        
        # Extract period data
        periods = result["periods"]
        expenses_by_period = result["total_expenses"]
        
        # Format response
        response = {
            "periods": periods,
            "expenses": [expenses_by_period.get(period, 0) for period in periods],
            "total_expenses": result["total_expenses_amount"]
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing expenses by period: {str(e)}")

@router.get("/by-supplier")
async def get_expenses_by_supplier(
    top_n: int = Query(10, description="Number of top suppliers to return")
):
    """
    Get expenses data grouped by supplier
    """
    try:
        # Get all expenses data
        result = financial_kpis_service.analyze_expenses_by_supplier(top_n=top_n)
        
        # Extract supplier data
        top_suppliers = result["top_suppliers"]
        
        return {"top_suppliers": top_suppliers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing expenses by supplier: {str(e)}")
