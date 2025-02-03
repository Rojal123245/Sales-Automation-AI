import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from typing import List, Dict

class ModelEvaluator:
    def __init__(self, config: Dict):
        self.config = config
        self.results = {}

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(
            self.config['data']['input_path'],
            parse_dates=[self.config['features']['date_col']]
        )
    
    def adf_test(self, series):
        result = adfuller(series)
        self.results['adf'] = {
            'statistic': result[0],
            'p-value': result[1],
            'used_lag': result[2],
            'n_obs': result[3],
            'critical_values': result[4]
        }
        return self
    
    def plot_sales_trend(self, df):
        plt.figure(figsize=(12, 6))
        df.groupby(self.config['features']['date_col'])['Sales'].sum().plot()
        plt.title('Sales Trend Analysis')
        plt.savefig('reports/sales_trend.png')
        plt.close()
        return self
    
    def generate_report(self):
        return {
            'stationarity_test': self.results['adf'],
            'plots': ['sales_trend.png']
        }