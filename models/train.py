import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA
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
    
    def grid_search_arima(self, series, p_values=range(0,3), 
                         d_values=range(0,2), q_values=range(0,3)):
        best_aic = float("inf")
        best_order = None
        best_model = None

        for p in p_values:
            for d in d_values:
                for q in q_values:
                    try:
                        model = ARIMA(series, order=(p,d,q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_order = (p,d,q)
                            best_model = results
                    except:
                        continue
        return best_order, best_model
    
    def initialize_model(self):
        try:
                train_size = int(len(self.data) * 0.8)
                self.train = self.data[:train_size]
                self.test = self.data[train_size:]
                
                # Find best order
                best_order, _ = self.grid_search_arima(self.train['Sales'])
                self.logger.info(f"Best ARIMA order: {best_order}")
                
                # Initialize model with exogenous variables
                self.model = ARIMA(
                    endog=self.train['Sales'],
                    exog=self.train[self.features],
                    order=best_order
                )
        except KeyError as e:
                self.logger.error(f"Missing feature in preprocessed data: {e}")
                raise
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