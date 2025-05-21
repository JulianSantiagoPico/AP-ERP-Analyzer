from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.financial_kpis_service import financial_kpis_service

router = APIRouter()

@router.get("/")
async def get_sales_analysis(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    third_party_id: Optional[int] = Query(None, description="Filter by third party ID")
):
    """
    Get sales analysis including total sales, sales growth, and top customers
    """
    try:
        result = financial_kpis_service.analyze_sales(year=year, month=month, third_party_id=third_party_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sales: {str(e)}")

@router.get("/by-period")
async def get_sales_by_period():
    """
    Get sales data grouped by period for trend analysis
    """
    try:
        # Get all sales data
        result = financial_kpis_service.analyze_sales()
        
        # Extract period data
        periods = result["periods"]
        sales_by_period = result["total_sales"]
        growth_by_period = result["sales_growth"]
        
        # Format response
        response = {
            "periods": periods,
            "sales": [sales_by_period.get(period, 0) for period in periods],
            "growth": [growth_by_period.get(period, 0) for period in periods]
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sales by period: {str(e)}")

@router.get("/by-customer")
async def get_sales_by_customer(
    top_n: int = Query(10, description="Number of top customers to return")
):
    """
    Get sales data grouped by customer
    """
    try:
        # Get all sales data
        result = financial_kpis_service.analyze_sales()
        
        # Extract customer data
        top_customers = result["top_customers"][:top_n]
        
        return {"top_customers": top_customers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sales by customer: {str(e)}")
