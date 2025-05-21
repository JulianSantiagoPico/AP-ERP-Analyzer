import pandas as pd
import os
from pathlib import Path

class DataLoader:
    """
    Service for loading and preprocessing ERP data
    """
    def __init__(self):
        self.base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_path = self.base_path / "data"
        self._account_balances = None
    
    @property
    def account_balances(self):
        """
        Load and cache account balances data
        """
        if self._account_balances is None:
            file_path = self.data_path / "accounting_account_balances.csv"
            self._account_balances = pd.read_csv(file_path, dtype={'code': str})
            
            # Convert date columns to datetime
            for col in ['created_at', 'updated_at']:
                if col in self._account_balances.columns:
                    self._account_balances[col] = pd.to_datetime(self._account_balances[col])
            
            # Create period column for easier time-based analysis
            self._account_balances['period'] = self._account_balances['year'].astype(str) + '-' + \
                                              self._account_balances['month'].astype(str).str.zfill(2)
            
            # Create numeric period for time series analysis
            self._account_balances['numeric_period'] = self._account_balances['year'] * 12 + self._account_balances['month']
            
            # Ensure only the code column is string type for string operations
            # This keeps numeric columns as numbers for calculations
            if 'code' in self._account_balances.columns:
                self._account_balances['code'] = self._account_balances['code'].astype(str)
        
        return self._account_balances
    
    def get_filtered_data(self, account_type=None, year=None, month=None, third_party_id=None):
        """
        Get filtered account balances data based on specified criteria
        
        Parameters:
        -----------
        account_type : str, optional
            Filter by account type (e.g., 'Activo', 'Pasivos')
        year : int, optional
            Filter by year
        month : int, optional
            Filter by month
        third_party_id : int, optional
            Filter by third party ID
            
        Returns:
        --------
        pandas.DataFrame
            Filtered account balances data
        """
        data = self.account_balances.copy()
        
        if account_type:
            data = data[data['name'] == account_type]
        
        if year:
            data = data[data['year'] == year]
            
        if month:
            data = data[data['month'] == month]
            
        if third_party_id:
            data = data[data['third_party_id'] == third_party_id]
            
        return data
    
    def get_unique_periods(self):
        """
        Get unique time periods in the data
        
        Returns:
        --------
        list
            List of unique periods in format 'YYYY-MM'
        """
        return sorted(self.account_balances['period'].unique().tolist())
    
    def get_unique_account_types(self):
        """
        Get unique account types in the data
        
        Returns:
        --------
        list
            List of unique account types
        """
        return sorted(self.account_balances['name'].unique().tolist())
    
    def get_unique_third_parties(self):
        """
        Get unique third parties in the data
        
        Returns:
        --------
        list
            List of unique third party IDs
        """
        return sorted(self.account_balances['third_party_id'].unique().tolist())

# Singleton instance
data_loader = DataLoader()
