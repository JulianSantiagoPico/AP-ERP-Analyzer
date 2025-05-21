import pandas as pd
import numpy as np
from app.services.data_loader import data_loader

class FinancialKPIsService:
    """
    Service for calculating financial KPIs based on ERP data
    """
    def __init__(self):
        self.data_loader = data_loader
    
    def calculate_cash_flow(self, year=None, month=None):
        """
        Calculate cash flow KPIs
        
        Parameters:
        -----------
        year : int, optional
            Filter by year
        month : int, optional
            Filter by month
            
        Returns:
        --------
        dict
            Dictionary containing cash flow KPIs
        """
        # Get data
        df = self.data_loader.account_balances.copy()
        
        # Filter by year and month if provided
        if year:
            df = df[df['year'] == year]
        if month:
            df = df[df['month'] == month]
        
        # Group by period for time series analysis
        period_df = df.groupby(['year', 'month', 'period']).agg({
            'debit_movement': 'sum',
            'credit_movement': 'sum',
            'final_balance': 'sum'
        }).reset_index()
        
        # Sort by period
        period_df = period_df.sort_values(['year', 'month'])
        
        # Calculate cash flow components
        # For this example, we'll use a simplified approach:
        # - Operating cash flow: Transactions related to main business operations
        # - Investment cash flow: Transactions related to long-term assets
        # - Financing cash flow: Transactions related to debt and equity
        
        # Get operating accounts (simplified approach)
        operating_df = df[df['code'].str.startswith(('4', '5', '6'))]
        operating_cash_flow = operating_df.groupby(['year', 'month', 'period']).agg({
            'debit_movement': 'sum',
            'credit_movement': 'sum'
        }).reset_index()
        operating_cash_flow['net_flow'] = operating_cash_flow['credit_movement'] - operating_cash_flow['debit_movement']
        
        # Get investment accounts (simplified approach)
        investment_df = df[df['code'].str.startswith('1.2')]
        investment_cash_flow = investment_df.groupby(['year', 'month', 'period']).agg({
            'debit_movement': 'sum',
            'credit_movement': 'sum'
        }).reset_index()
        investment_cash_flow['net_flow'] = investment_cash_flow['credit_movement'] - investment_cash_flow['debit_movement']
        
        # Get financing accounts (simplified approach)
        financing_df = df[df['code'].str.startswith(('2.1', '2.2', '3'))]
        financing_cash_flow = financing_df.groupby(['year', 'month', 'period']).agg({
            'debit_movement': 'sum',
            'credit_movement': 'sum'
        }).reset_index()
        financing_cash_flow['net_flow'] = financing_cash_flow['credit_movement'] - financing_cash_flow['debit_movement']
        
        # Prepare result
        result = {
            'periods': period_df['period'].tolist(),
            'operating_cash_flow': operating_cash_flow.set_index('period')['net_flow'].to_dict(),
            'investment_cash_flow': investment_cash_flow.set_index('period')['net_flow'].to_dict(),
            'financing_cash_flow': financing_cash_flow.set_index('period')['net_flow'].to_dict(),
        }
        
        # Calculate accumulated cash flow
        accumulated_flow = {}
        total_flow = 0
        
        for period in result['periods']:
            operating = result['operating_cash_flow'].get(period, 0)
            investment = result['investment_cash_flow'].get(period, 0)
            financing = result['financing_cash_flow'].get(period, 0)
            
            period_flow = operating + investment + financing
            total_flow += period_flow
            accumulated_flow[period] = total_flow
        
        result['accumulated_cash_flow'] = accumulated_flow
        result['total_cash_flow'] = {
            period: (
                result['operating_cash_flow'].get(period, 0) + 
                result['investment_cash_flow'].get(period, 0) + 
                result['financing_cash_flow'].get(period, 0)
            ) for period in result['periods']
        }
        
        return result
    
    def analyze_sales(self, year=None, month=None, third_party_id=None):
        """
        Analyze sales data
        
        Parameters:
        -----------
        year : int, optional
            Filter by year
        month : int, optional
            Filter by month
        third_party_id : int, optional
            Filter by third party ID
            
        Returns:
        --------
        dict
            Dictionary containing sales analysis KPIs
        """
        # Get data
        df = self.data_loader.account_balances.copy()
        
        # Filter by year and month if provided
        if year:
            df = df[df['year'] == year]
        if month:
            df = df[df['month'] == month]
        if third_party_id:
            df = df[df['third_party_id'] == third_party_id]
        
        # Filter for revenue accounts (code starting with 4)
        sales_df = df[df['code'].str.startswith('4')]
        
        # Group by period for time series analysis
        period_sales = sales_df.groupby(['year', 'month', 'period']).agg({
            'credit_movement': 'sum'  # Credit movements represent revenue
        }).reset_index()
        
        # Group by third party for customer analysis
        customer_sales = sales_df.groupby(['third_party_id', 'third_party_type_id']).agg({
            'credit_movement': 'sum'
        }).reset_index().sort_values('credit_movement', ascending=False)
        
        # Calculate sales growth
        period_sales = period_sales.sort_values(['year', 'month'])
        period_sales['previous_sales'] = period_sales['credit_movement'].shift(1)
        period_sales['sales_growth'] = (period_sales['credit_movement'] - period_sales['previous_sales']) / period_sales['previous_sales'] * 100
        period_sales['sales_growth'] = period_sales['sales_growth'].fillna(0)
        
        # Prepare result
        result = {
            'periods': period_sales['period'].tolist(),
            'total_sales': period_sales.set_index('period')['credit_movement'].to_dict(),
            'sales_growth': period_sales.set_index('period')['sales_growth'].to_dict(),
            'top_customers': customer_sales.head(10).to_dict(orient='records'),
            'total_sales_amount': sales_df['credit_movement'].sum()
        }
        
        return result
    
    def analyze_accounts_receivable_payable(self, year=None, month=None):
        """
        Analyze accounts receivable and payable
        
        Parameters:
        -----------
        year : int, optional
            Filter by year
        month : int, optional
            Filter by month
            
        Returns:
        --------
        dict
            Dictionary containing accounts receivable and payable KPIs
        """
        # Get data
        df = self.data_loader.account_balances.copy()
        
        # Filter by year and month if provided
        if year:
            df = df[df['year'] == year]
        if month:
            df = df[df['month'] == month]
        
        # Filter for accounts receivable (code starting with 1.3)
        receivables_df = df[df['code'].str.startswith('1.3')]
        
        # Filter for accounts payable (code starting with 2.1 or 2.2)
        payables_df = df[df['code'].str.startswith(('2.1', '2.2'))]
        
        # Group by period for time series analysis
        period_receivables = receivables_df.groupby(['year', 'month', 'period']).agg({
            'final_balance': 'sum'
        }).reset_index()
        
        period_payables = payables_df.groupby(['year', 'month', 'period']).agg({
            'final_balance': 'sum'
        }).reset_index()
        
        # Calculate average balances
        avg_receivables = receivables_df['final_balance'].mean()
        avg_payables = payables_df['final_balance'].mean()
        
        # Calculate receivables turnover (simplified)
        # Ideally, we would use sales / average receivables
        sales_df = df[df['code'].str.startswith('4')]
        total_sales = sales_df['credit_movement'].sum()
        
        if avg_receivables > 0:
            receivables_turnover = total_sales / avg_receivables
            days_sales_outstanding = 365 / receivables_turnover if receivables_turnover > 0 else 0
        else:
            receivables_turnover = 0
            days_sales_outstanding = 0
        
        # Calculate payables turnover (simplified)
        # Ideally, we would use purchases / average payables
        purchases_df = df[df['code'].str.startswith('6')]  # Cost of goods sold
        total_purchases = purchases_df['debit_movement'].sum()
        
        if avg_payables > 0:
            payables_turnover = total_purchases / avg_payables
            days_payables_outstanding = 365 / payables_turnover if payables_turnover > 0 else 0
        else:
            payables_turnover = 0
            days_payables_outstanding = 0
        
        # Prepare result
        result = {
            'periods': sorted(set(period_receivables['period'].tolist() + period_payables['period'].tolist())),
            'accounts_receivable': period_receivables.set_index('period')['final_balance'].to_dict(),
            'accounts_payable': period_payables.set_index('period')['final_balance'].to_dict(),
            'avg_accounts_receivable': float(avg_receivables),
            'avg_accounts_payable': float(avg_payables),
            'receivables_turnover': float(receivables_turnover),
            'days_sales_outstanding': float(days_sales_outstanding),
            'payables_turnover': float(payables_turnover),
            'days_payables_outstanding': float(days_payables_outstanding)
        }
        
        return result
    
    def analyze_expenses_by_supplier(self, year=None, month=None, top_n=10):
        """
        Analyze expenses by supplier
        
        Parameters:
        -----------
        year : int, optional
            Filter by year
        month : int, optional
            Filter by month
        top_n : int, optional
            Number of top suppliers to return
            
        Returns:
        --------
        dict
            Dictionary containing expenses by supplier KPIs
        """
        # Get data
        df = self.data_loader.account_balances.copy()
        
        # Filter by year and month if provided
        if year:
            df = df[df['year'] == year]
        if month:
            df = df[df['month'] == month]
        
        # Filter for expense accounts (code starting with 5 or 6)
        expenses_df = df[df['code'].str.startswith(('5', '6'))]
        
        # Group by supplier
        supplier_expenses = expenses_df.groupby(['third_party_id', 'third_party_type_id']).agg({
            'debit_movement': 'sum'  # Debit movements represent expenses
        }).reset_index().sort_values('debit_movement', ascending=False)
        
        # Group by period for time series analysis
        period_expenses = expenses_df.groupby(['year', 'month', 'period']).agg({
            'debit_movement': 'sum'
        }).reset_index().sort_values(['year', 'month'])
        
        # Calculate total expenses
        total_expenses = expenses_df['debit_movement'].sum()
        
        # Calculate percentage of total for each supplier
        if total_expenses > 0:
            supplier_expenses['percentage'] = supplier_expenses['debit_movement'] / total_expenses * 100
        else:
            supplier_expenses['percentage'] = 0
        
        # Get top suppliers
        top_suppliers = supplier_expenses.head(top_n).to_dict(orient='records')
        
        # Prepare result
        result = {
            'periods': period_expenses['period'].tolist(),
            'total_expenses': period_expenses.set_index('period')['debit_movement'].to_dict(),
            'top_suppliers': top_suppliers,
            'total_expenses_amount': float(total_expenses)
        }
        
        return result

# Singleton instance
financial_kpis_service = FinancialKPIsService()
