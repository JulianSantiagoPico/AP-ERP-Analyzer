import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import IsolationForest
import joblib
import os
from pathlib import Path
from app.services.data_loader import data_loader

class MLService:
    """
    Service for machine learning models and predictions
    """
    def __init__(self):
        self.data_loader = data_loader
        self.base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.models_path = self.base_path / "models"
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_path, exist_ok=True)
        
        # Model file paths
        self.sales_forecast_model_path = self.models_path / "sales_forecast_model.pkl"
        self.anomaly_detection_model_path = self.models_path / "anomaly_detection_model.pkl"
    
    def train_sales_forecast_model(self, force_retrain=False):
        """
        Train a sales forecast model using ARIMA/SARIMA
        
        Parameters:
        -----------
        force_retrain : bool, optional
            Force retraining of the model even if it already exists
            
        Returns:
        --------
        dict
            Training results
        """
        # Check if model already exists and we're not forcing a retrain
        if os.path.exists(self.sales_forecast_model_path) and not force_retrain:
            return {"message": "Model already exists. Use force_retrain=True to retrain."}
        
        # Get sales data
        df = self.data_loader.account_balances.copy()
        
        # Filter for revenue accounts (code starting with 4)
        sales_df = df[df['code'].str.startswith('4')]
        
        # Group by period for time series analysis
        period_sales = sales_df.groupby(['year', 'month', 'numeric_period']).agg({
            'credit_movement': 'sum'  # Credit movements represent revenue
        }).reset_index().sort_values('numeric_period')
        
        # Prepare time series data
        ts_data = period_sales.set_index('numeric_period')['credit_movement']
        
        # Check if we have enough data
        if len(ts_data) < 4:
            return {"error": "Not enough data to train a time series model. Need at least 4 periods."}
        
        try:
            # Try SARIMA model first (seasonal ARIMA)
            model = SARIMAX(ts_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
            model_fit = model.fit(disp=False)
            
            # Save the model
            joblib.dump({
                'model': model_fit,
                'last_period': ts_data.index[-1],
                'data': ts_data
            }, self.sales_forecast_model_path)
            
            return {
                "message": "Sales forecast model trained successfully",
                "model_type": "SARIMA",
                "periods_used": len(ts_data)
            }
        
        except Exception as e:
            # If SARIMA fails, try simple ARIMA
            try:
                model = ARIMA(ts_data, order=(1, 1, 1))
                model_fit = model.fit()
                
                # Save the model
                joblib.dump({
                    'model': model_fit,
                    'last_period': ts_data.index[-1],
                    'data': ts_data
                }, self.sales_forecast_model_path)
                
                return {
                    "message": "Sales forecast model trained successfully",
                    "model_type": "ARIMA",
                    "periods_used": len(ts_data)
                }
            
            except Exception as e2:
                return {
                    "error": f"Failed to train sales forecast model: {str(e2)}",
                    "sarima_error": str(e)
                }
    
    def predict_sales(self, periods=3):
        """
        Predict future sales
        
        Parameters:
        -----------
        periods : int, optional
            Number of periods to forecast
            
        Returns:
        --------
        dict
            Sales forecast results
        """
        # Check if model exists
        if not os.path.exists(self.sales_forecast_model_path):
            # Train model if it doesn't exist
            training_result = self.train_sales_forecast_model()
            if "error" in training_result:
                return training_result
        
        try:
            # Load the model
            model_data = joblib.load(self.sales_forecast_model_path)
            model = model_data['model']
            last_period = model_data['last_period']
            historical_data = model_data['data']
            
            # Make forecast
            forecast = model.forecast(steps=periods)
            forecast_index = range(last_period + 1, last_period + periods + 1)
            
            # Convert forecast to dictionary
            forecast_dict = {idx: val for idx, val in zip(forecast_index, forecast)}
            
            # Convert numeric periods to year-month format
            period_mapping = {}
            for idx in forecast_index:
                year = idx // 12
                month = idx % 12
                if month == 0:
                    month = 12
                    year -= 1
                period_mapping[idx] = f"{year}-{month:02d}"
            
            # Prepare result with confidence intervals
            result = {
                "forecast_periods": [period_mapping[idx] for idx in forecast_index],
                "forecast_values": [float(val) for val in forecast],
                "historical_periods": [period_mapping.get(idx, f"{idx//12}-{idx%12:02d}") for idx in historical_data.index],
                "historical_values": [float(val) for val in historical_data.values],
            }
            
            return result
        
        except Exception as e:
            return {"error": f"Failed to predict sales: {str(e)}"}
    
    def train_anomaly_detection_model(self, force_retrain=False):
        """
        Train an anomaly detection model for cash flow
        
        Parameters:
        -----------
        force_retrain : bool, optional
            Force retraining of the model even if it already exists
            
        Returns:
        --------
        dict
            Training results
        """
        # Check if model already exists and we're not forcing a retrain
        if os.path.exists(self.anomaly_detection_model_path) and not force_retrain:
            return {"message": "Model already exists. Use force_retrain=True to retrain."}
        
        # Get cash flow data
        df = self.data_loader.account_balances.copy()
        
        # Calculate daily net cash flow (simplified)
        cash_flow_df = df.groupby(['year', 'month', 'numeric_period']).agg({
            'debit_movement': 'sum',
            'credit_movement': 'sum'
        }).reset_index()
        
        cash_flow_df['net_flow'] = cash_flow_df['credit_movement'] - cash_flow_df['debit_movement']
        
        # Check if we have enough data
        if len(cash_flow_df) < 10:
            return {"error": "Not enough data to train an anomaly detection model. Need at least 10 periods."}
        
        try:
            # Prepare features for anomaly detection
            X = cash_flow_df[['net_flow']].values
            
            # Train Isolation Forest model
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X)
            
            # Save the model
            joblib.dump({
                'model': model,
                'data': cash_flow_df
            }, self.anomaly_detection_model_path)
            
            return {
                "message": "Anomaly detection model trained successfully",
                "model_type": "IsolationForest",
                "periods_used": len(cash_flow_df)
            }
        
        except Exception as e:
            return {"error": f"Failed to train anomaly detection model: {str(e)}"}
    
    def detect_anomalies(self):
        """
        Detect anomalies in cash flow
        
        Returns:
        --------
        dict
            Anomaly detection results
        """
        # Check if model exists
        if not os.path.exists(self.anomaly_detection_model_path):
            # Train model if it doesn't exist
            training_result = self.train_anomaly_detection_model()
            if "error" in training_result:
                return training_result
        
        try:
            # Load the model
            model_data = joblib.load(self.anomaly_detection_model_path)
            model = model_data['model']
            cash_flow_df = model_data['data'].copy()
            
            # Prepare features for anomaly detection
            X = cash_flow_df[['net_flow']].values
            
            # Predict anomalies
            # -1 for anomalies, 1 for normal points
            predictions = model.predict(X)
            anomaly_scores = model.decision_function(X)
            
            # Add predictions to dataframe
            cash_flow_df['is_anomaly'] = predictions == -1
            cash_flow_df['anomaly_score'] = anomaly_scores
            
            # Create period column for output
            cash_flow_df['period'] = cash_flow_df['year'].astype(str) + '-' + cash_flow_df['month'].astype(str).str.zfill(2)
            
            # Get anomalies
            anomalies = cash_flow_df[cash_flow_df['is_anomaly']].sort_values('anomaly_score')
            
            # Prepare result
            result = {
                "periods": cash_flow_df['period'].tolist(),
                "net_flow": cash_flow_df['net_flow'].tolist(),
                "is_anomaly": cash_flow_df['is_anomaly'].tolist(),
                "anomaly_score": cash_flow_df['anomaly_score'].tolist(),
                "anomalies": anomalies[['period', 'net_flow', 'anomaly_score']].to_dict(orient='records'),
                "anomaly_count": int(anomalies.shape[0])
            }
            
            return result
        
        except Exception as e:
            return {"error": f"Failed to detect anomalies: {str(e)}"}

# Singleton instance
ml_service = MLService()
