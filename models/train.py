import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Dict

class SalesForecastTrainer:
    def __init__(self, config: dict):
        self.config = config
        self.model = None

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(
            self.config['data']['input_path'],
            parse_dates=[self.config['features']['date_col']]
        )
    
    def initialize_model(self):
        order = self.config['model']['arima_order']
        self.model = ARIMAModel(
            endog = self.data['Sales'],
            order = order
        )

    def train(self):
        self.model_fit = self.model.fit()
        return self.model_fit
    
    def save_model(self):
        with open(self.config['model']['output_path'], 'wb') as f:
            pickle.dump(self.model_fit, f)
        print(f"Model saved to {self.config['model']['output_path']}")

    def full_pipeline(self):
        self.data = self.load_data()
        self.initialize_model()
        self.train()
        self.save_model()
        return self.model_fit