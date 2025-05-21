from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class CashFlowResponse(BaseModel):
    """Model for cash flow analysis response"""
    periods: List[str]
    operating_cash_flow: Dict[str, float]
    investment_cash_flow: Dict[str, float]
    financing_cash_flow: Dict[str, float]
    accumulated_cash_flow: Dict[str, float]
    total_cash_flow: Dict[str, float]

class SalesAnalysisResponse(BaseModel):
    """Model for sales analysis response"""
    periods: List[str]
    total_sales: Dict[str, float]
    sales_growth: Dict[str, float]
    top_customers: List[Dict[str, Any]]
    total_sales_amount: float

class CustomerSalesResponse(BaseModel):
    """Model for customer sales analysis response"""
    third_party_id: int
    third_party_type_id: str
    credit_movement: float
    percentage: Optional[float] = None

class AccountsAnalysisResponse(BaseModel):
    """Model for accounts receivable and payable analysis response"""
    periods: List[str]
    accounts_receivable: Dict[str, float]
    accounts_payable: Dict[str, float]
    avg_accounts_receivable: float
    avg_accounts_payable: float
    receivables_turnover: float
    days_sales_outstanding: float
    payables_turnover: float
    days_payables_outstanding: float

class ExpensesAnalysisResponse(BaseModel):
    """Model for expenses analysis response"""
    periods: List[str]
    total_expenses: Dict[str, float]
    top_suppliers: List[Dict[str, Any]]
    total_expenses_amount: float

class SupplierExpensesResponse(BaseModel):
    """Model for supplier expenses analysis response"""
    third_party_id: int
    third_party_type_id: str
    debit_movement: float
    percentage: Optional[float] = None

class FinancialSummaryResponse(BaseModel):
    """Model for financial summary response"""
    periods: List[str]
    total_sales: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    accounts_receivable: float
    accounts_payable: float
    days_sales_outstanding: float
    days_payables_outstanding: float
    cash_flow_summary: Dict[str, float]
