import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Dict, Tuple
import ast

class SalesForecastTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.model = None

    def _parse_order(self, order: str) -> Tuple[int, int, int]:
        try:
            return ast.literal_eval(order)
        except:
            raise ValueError(f"Invalid ARIMA order format: {order}")

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(
            self.config['data']['input_path'],
            parse_dates=[self.config['features']['date_col']]
        )
    
    def initialize_model(self):
        order = self._parse_order(self.config['model']['arima_order'])
        self.model = ARIMA(
            endog = self.data['Sales'],
            order = order
        )

    def train(self):
        self.model_fit = self.model.fit()
        return self.model_fit
    
    def save_model(self):
        with open(self.config['model']['save_path'], 'wb') as f:
            pickle.dump(self.model_fit, f)
        print(f"Model saved to {self.config['model']['save_path']}")

    def full_pipeline(self):
        self.data = self.load_data()
        self.initialize_model()
        self.train()
        self.save_model()
        return self.model_fit