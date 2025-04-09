import pandas as pd
import pickle
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import List, Dict, Tuple
import ast
import logging

class SalesForecastTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.logger = logging.getLogger(__name__)
        self.features = ['dayofweek', 'month', 'quarter', 'is_weekend', 
                        'stock_ratio', 'price_bins', 'sales_ratio',
                        'sales_lag1', 'sales_lag7', 'sales_ma_7d', 
                        'sales_ma_30d', 'price_stock_ratio', 'sales_price_ratio']
    

    def _parse_order(self, order: str) -> Tuple[int, int, int]:
        try:
            return ast.literal_eval(order)
        except:
            raise ValueError(f"Invalid ARIMA order format: {order}")

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(
            self.config['data']['output_path'],
            parse_dates=[self.config['features']['date_col']]
        )
    
    def grid_search_sarimax(self, data):
        """
        Perform grid search for best SARIMA parameters
        """
        p = range(0, 3)
        d = range(0, 2)
        q = range(0, 3)
        P = range(0, 2)
        D = range(0, 2)
        Q = range(0, 2)
        s = [12]  # Monthly seasonality
        
        best_aic = float('inf')
        best_order = None
        best_seasonal_order = None
        
        for p_val in p:
            for d_val in d:
                for q_val in q:
                    for P_val in P:
                        for D_val in D:
                            for Q_val in Q:
                                for s_val in s:
                                    try:
                                        model = SARIMAX(
                                            data,
                                            order=(p_val, d_val, q_val),
                                            seasonal_order=(P_val, D_val, Q_val, s_val),
                                            enforce_stationarity=False,
                                            enforce_invertibility=False
                                        )
                                        results = model.fit(disp=0)
                                        if results.aic < best_aic:
                                            best_aic = results.aic
                                            best_order = (p_val, d_val, q_val)
                                            best_seasonal_order = (P_val, D_val, Q_val, s_val)
                                    except:
                                        continue
        
        return best_order, best_seasonal_order
    
    def initialize_model(self):
        try:
            train_size = int(len(self.data) * 0.8)
            self.train = self.data[:train_size]
            self.test = self.data[train_size:]
            
            # Grid search for best parameters
            best_order, best_seasonal_order = self.grid_search_sarimax(self.train['Sales'])
            self.logger.info(f"Best SARIMA order: {best_order}, seasonal_order: {best_seasonal_order}")
            
            # Initialize model with exogenous variables and seasonal components
            self.model = SARIMAX(
                endog=self.train['Sales'],
                exog=self.train[self.features],
                order=best_order,
                seasonal_order=best_seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
        except Exception as e:
            self.logger.error(f"Error initializing model: {e}")
            raise

    def fit_model(self):
        self.model_fit = self.model.fit()
        return self.model_fit
    
    def save_model(self):
        with open(self.config['model']['save_path'], 'wb') as f:
            pickle.dump(self.model_fit, f)
        print(f"Model saved to {self.config['model']['save_path']}")

    def full_pipeline(self):
        self.data = self.load_data()
        self.initialize_model()
        self.fit_model()
        self.save_model()
        return self.model_fit
    
