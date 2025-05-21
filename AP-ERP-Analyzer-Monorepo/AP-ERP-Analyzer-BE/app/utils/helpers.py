import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

def format_currency(value: float) -> str:
    """
    Format a value as currency (COP)
    
    Parameters:
    -----------
    value : float
        Value to format
        
    Returns:
    --------
    str
        Formatted currency string
    """
    return f"${value:,.2f} COP"

def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate growth rate between two values
    
    Parameters:
    -----------
    current : float
        Current value
    previous : float
        Previous value
        
    Returns:
    --------
    float
        Growth rate as percentage
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100

def calculate_moving_average(data: List[float], window: int = 3) -> List[float]:
    """
    Calculate moving average of a list of values
    
    Parameters:
    -----------
    data : List[float]
        List of values
    window : int, optional
        Window size for moving average
        
    Returns:
    --------
    List[float]
        Moving average values
    """
    if len(data) < window:
        return data
    
    result = []
    for i in range(len(data)):
        if i < window - 1:
            result.append(np.nan)
        else:
            window_avg = np.mean(data[i-(window-1):i+1])
            result.append(window_avg)
    
    return result

def calculate_year_over_year_growth(data: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate year-over-year growth for time series data
    
    Parameters:
    -----------
    data : Dict[str, float]
        Dictionary with period keys (YYYY-MM) and values
        
    Returns:
    --------
    Dict[str, float]
        Dictionary with period keys and YoY growth values
    """
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(list(data.items()), columns=['period', 'value'])
    
    # Extract year and month
    df[['year', 'month']] = df['period'].str.split('-', expand=True).astype(int)
    
    # Sort by year and month
    df = df.sort_values(['year', 'month'])
    
    # Calculate YoY growth
    df['prev_year_value'] = df.apply(
        lambda x: df[(df['year'] == x['year'] - 1) & (df['month'] == x['month'])]['value'].values[0] 
        if any((df['year'] == x['year'] - 1) & (df['month'] == x['month'])) else np.nan, 
        axis=1
    )
    
    df['yoy_growth'] = df.apply(
        lambda x: calculate_growth_rate(x['value'], x['prev_year_value']) if not np.isnan(x['prev_year_value']) else np.nan,
        axis=1
    )
    
    # Convert back to dictionary
    result = {period: growth for period, growth in zip(df['period'], df['yoy_growth']) if not np.isnan(growth)}
    
    return result

def detect_outliers(data: List[float], threshold: float = 1.5) -> List[bool]:
    """
    Detect outliers in a list of values using IQR method
    
    Parameters:
    -----------
    data : List[float]
        List of values
    threshold : float, optional
        Threshold multiplier for IQR
        
    Returns:
    --------
    List[bool]
        List of booleans indicating if each value is an outlier
    """
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)
    
    return [x < lower_bound or x > upper_bound for x in data]
