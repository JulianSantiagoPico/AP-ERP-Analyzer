from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.financial_kpis_service import financial_kpis_service

router = APIRouter()

@router.get("/")
async def get_accounts_analysis(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month")
):
    """
    Get accounts receivable and payable analysis
    """
    try:
        result = financial_kpis_service.analyze_accounts_receivable_payable(year=year, month=month)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing accounts: {str(e)}")

@router.get("/receivable")
async def get_accounts_receivable(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month")
):
    """
    Get accounts receivable analysis
    """
    try:
        # Get all accounts data
        result = financial_kpis_service.analyze_accounts_receivable_payable(year=year, month=month)
        
        # Extract receivables data
        periods = result["periods"]
        receivables_by_period = result["accounts_receivable"]
        
        # Format response
        response = {
            "periods": periods,
            "receivables": [receivables_by_period.get(period, 0) for period in periods],
            "avg_receivables": result["avg_accounts_receivable"],
            "days_sales_outstanding": result["days_sales_outstanding"],
            "receivables_turnover": result["receivables_turnover"]
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing accounts receivable: {str(e)}")

@router.get("/payable")
async def get_accounts_payable(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month")
):
    """
    Get accounts payable analysis
    """
    try:
        # Get all accounts data
        result = financial_kpis_service.analyze_accounts_receivable_payable(year=year, month=month)
        
        # Extract payables data
        periods = result["periods"]
        payables_by_period = result["accounts_payable"]
        
        # Format response
        response = {
            "periods": periods,
            "payables": [payables_by_period.get(period, 0) for period in periods],
            "avg_payables": result["avg_accounts_payable"],
            "days_payables_outstanding": result["days_payables_outstanding"],
            "payables_turnover": result["payables_turnover"]
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing accounts payable: {str(e)}")
