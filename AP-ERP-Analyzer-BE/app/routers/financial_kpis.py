from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.financial_kpis_service import financial_kpis_service

router = APIRouter()

@router.get("/cash-flow")
async def get_cash_flow(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month")
):
    """
    Get cash flow KPIs including operating, investment, financing, and accumulated cash flows
    """
    try:
        result = financial_kpis_service.calculate_cash_flow(year=year, month=month)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating cash flow: {str(e)}")

@router.get("/summary")
async def get_financial_summary(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month")
):
    """
    Get a summary of key financial indicators
    """
    try:
        # Get cash flow data
        cash_flow = financial_kpis_service.calculate_cash_flow(year=year, month=month)
        
        # Get sales data
        sales = financial_kpis_service.analyze_sales(year=year, month=month)
        
        # Get accounts receivable/payable data
        accounts = financial_kpis_service.analyze_accounts_receivable_payable(year=year, month=month)
        
        # Get expenses data
        expenses = financial_kpis_service.analyze_expenses_by_supplier(year=year, month=month)
        
        # Compile summary
        summary = {
            "periods": cash_flow["periods"],
            "total_sales": sales["total_sales_amount"],
            "total_expenses": expenses["total_expenses_amount"],
            "net_profit": sales["total_sales_amount"] - expenses["total_expenses_amount"],
            "profit_margin": (sales["total_sales_amount"] - expenses["total_expenses_amount"]) / sales["total_sales_amount"] * 100 if sales["total_sales_amount"] > 0 else 0,
            "accounts_receivable": accounts["avg_accounts_receivable"],
            "accounts_payable": accounts["avg_accounts_payable"],
            "days_sales_outstanding": accounts["days_sales_outstanding"],
            "days_payables_outstanding": accounts["days_payables_outstanding"],
            "cash_flow_summary": {
                "operating": sum(cash_flow["operating_cash_flow"].values()),
                "investment": sum(cash_flow["investment_cash_flow"].values()),
                "financing": sum(cash_flow["financing_cash_flow"].values()),
                "total": sum(cash_flow["total_cash_flow"].values())
            }
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating financial summary: {str(e)}")
