import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from typing import List, Dict
import logging

class ModelEvaluator:
    def __init__(self, config: Dict):
        self.config = config
        self.results = {}
        self.logger = logging.getLogger(__name__)
        self.features = ['dayofweek', 'month', 'quarter', 'is_weekend', 
                        'stock_ratio', 'price_bins', 'sales_ratio',
                        'sales_lag1', 'sales_lag7', 'sales_ma_7d', 
                        'sales_ma_30d', 'price_stock_ratio', 'sales_price_ratio']
        self.data = None
        self.train_data = None
        self.test_data = None
        self.forecast = None

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(
            self.config['data']['output_path'],
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

    def plot_forecast(self, df: pd.DataFrame, model):
        try:
        # Prepare data
            self.data = df
            train_size = int(len(df) * 0.8)
            self.train_data = df[:train_size]
            self.test_data = df[train_size:]
            
            # Validate features
            missing_features = [f for f in self.features if f not in self.test_data.columns]
            if missing_features:
                raise KeyError(f"Missing features in test data: {missing_features}")
            
            # Generate forecast with exogenous variables
            self.forecast = model.forecast(
                steps=len(self.test_data), 
                exog=self.test_data[self.features]
            )
            
            # Create visualization
            plt.figure(figsize=(15, 8))
            
            # Plot data
            plt.plot(self.train_data.index[-30:], 
                    self.train_data['Sales'][-30:], 
                    'b-', label='Training Data')
            plt.plot(self.test_data.index[:30], 
                    self.test_data['Sales'][:30], 
                    'g-', label='Actual Values')
            plt.plot(self.test_data.index[:30], 
                    self.forecast[:30], 
                    'r--', label='Forecast')
            
            # Add confidence intervals
            if hasattr(model, 'get_forecast'):
                try:
                    forecast_obj = model.get_forecast(
                        steps=30,
                        exog=self.test_data[self.features][:30]  # Add exog for confidence intervals
                    )
                    conf_int = forecast_obj.conf_int()
                    plt.fill_between(
                        self.test_data.index[:30],
                        conf_int.iloc[:30, 0],
                        conf_int.iloc[:30, 1],
                        color='r', alpha=0.1,
                        label='95% Confidence Interval'
                    )
                except Exception as e:
                    self.logger.warning(f"Could not generate confidence intervals: {e}")
            
            # Style plot
            plt.title('Sales Forecast Analysis', fontsize=12)
            plt.xlabel('Date', fontsize=10)
            plt.ylabel('Sales', fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(loc='best')
            plt.xticks(rotation=45)
            
            # Save plot
            plt.tight_layout()
            plt.savefig('reports/forecast.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Calculate and store metrics
            rmse = np.sqrt(((self.test_data['Sales'][:30] - self.forecast[:30]) ** 2).mean())
            mae = np.mean(np.abs(self.test_data['Sales'][:30] - self.forecast[:30]))
            mape = np.mean(np.abs((self.test_data['Sales'][:30] - self.forecast[:30]) / self.test_data['Sales'][:30])) * 100
            
            self.results['metrics'] = {
                'rmse': np.sqrt(((self.test_data['Sales'][:30] - self.forecast[:30]) ** 2).mean()),
                'mae': np.mean(np.abs(self.test_data['Sales'][:30] - self.forecast[:30])),
                'mape': np.mean(np.abs((self.test_data['Sales'][:30] - self.forecast[:30]) / 
                                     self.test_data['Sales'][:30])) * 100,
                'forecast_length': len(self.forecast)
            }
            
            return self
            
        except Exception as e:
            self.logger.error(f"Error in plot_forecast: {str(e)}")
            raise

    
    def generate_report(self):
        """Generate comprehensive model evaluation report"""
        if not all([self.data is not None, self.train_data is not None, 
                   self.test_data is not None, self.forecast is not None]):
            raise ValueError("Must run plot_forecast before generating report")
            
        return {
            'stationarity_test': self.results.get('adf', {}),
            'performance_metrics': self.results.get('metrics', {}),
            'model_info': {
                'train_size': len(self.train_data),
                'test_size': len(self.test_data),
                'forecast_horizon': len(self.forecast)
            },
            'feature_importance': self._calculate_feature_importance(),
            'plots': ['sales_trend.png', 'forecast.png']
        }

    def _calculate_feature_importance(self):
        """Calculate feature importance using correlation with target"""
        correlations = {}
        for feature in self.features:
            corr = np.corrcoef(self.data[feature], self.data['Sales'])[0,1]
            correlations[feature] = abs(corr)
        return dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))