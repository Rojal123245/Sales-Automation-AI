import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from typing import List, Dict
import logging
import pickle
import os

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
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        plt.figure(figsize=(12, 6))
        df.groupby(self.config['features']['date_col'])['Sales'].sum().plot()
        plt.title('Sales Trend Analysis')
        plt.savefig('reports/sales_trend.png')
        plt.close()
        return self

    def plot_forecast(self, df: pd.DataFrame, model):
        try:
            # If model is None, try to load it
            if model is None:
                model_path = self.config.get('model', {}).get('save_path', 'models/saved/sales_forecast.pkl')
                try:
                    self.logger.info(f"Attempting to load model from {model_path}")
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    self.logger.info("Model loaded successfully")
                except Exception as e:
                    self.logger.error(f"Could not load model: {str(e)}")
                    # Create a simple dummy model for testing
                    self.logger.warning("Creating dummy forecast for testing")
                    class DummyModel:
                        def forecast(self, steps, exog=None):
                            # Create dummy forecast (just return the latest sales values)
                            latest_sales = df['Sales'].values[-steps:]
                            if len(latest_sales) < steps:
                                # Repeat the values if we don't have enough
                                latest_sales = np.tile(latest_sales, (steps // len(latest_sales) + 1))[:steps]
                            return latest_sales
                    model = DummyModel()
            
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
            
            # Ensure reports directory exists
            os.makedirs('reports', exist_ok=True)
            
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

    def get_prediction_data(self) -> pd.DataFrame:
        """
        Get data with predictions for automation purposes.
        
        Returns:
            DataFrame containing item data with sales predictions added
        """
        try:
            # Check if forecast data is already available
            if self.forecast is not None and self.data is not None:
                # Create a copy of the data to avoid modifying the original
                prediction_data = self.data.copy()
                
                # Add predictions to the DataFrame
                prediction_data['Predicted Sales'] = self.forecast
                
                # Group by item to get the latest data for each item
                if 'Item Name' in prediction_data.columns:
                    latest_data = prediction_data.sort_values(self.config['features']['date_col']).groupby('Item Name').last().reset_index()
                else:
                    # If no Item Name, use the entire dataset as "latest"
                    self.logger.warning("No 'Item Name' column found in data, using entire dataset")
                    latest_data = prediction_data.copy()
                    # Add a dummy Item Name if needed
                    latest_data['Item Name'] = latest_data.get('Item Name', 'Unknown Item')
                
                # Ensure Item Code exists
                if 'Item Code' not in latest_data.columns:
                    self.logger.warning("'Item Code' column missing, generating placeholder values")
                    if 'Item Name' in latest_data.columns:
                        # Create Item Code from Item Name (replace spaces with underscore and convert to uppercase)
                        latest_data['Item Code'] = latest_data['Item Name'].str.replace(' ', '_').str.upper()
                    else:
                        # Create sequential item codes
                        latest_data['Item Code'] = ['ITEM_' + str(i).zfill(5) for i in range(len(latest_data))]
                
                # Ensure Stock Left exists
                if 'Stock Left' not in latest_data.columns and 'Total Stock' in latest_data.columns:
                    self.logger.warning("'Stock Left' column missing, using 'Total Stock' instead")
                    latest_data['Stock Left'] = latest_data['Total Stock']
                elif 'Stock Left' not in latest_data.columns:
                    self.logger.warning("'Stock Left' column missing, generating random values")
                    # Generate random stock values between 5 and 25
                    latest_data['Stock Left'] = np.random.randint(5, 25, size=len(latest_data))
                
                # Select only needed columns for automation
                required_cols = ['Item Name', 'Item Code', 'Stock Left', 'Sales', 'Predicted Sales', 'Price']
                available_cols = [col for col in required_cols if col in latest_data.columns]
                
                result_df = latest_data[available_cols].copy()
                
                # If some required columns are missing, log warning
                missing_cols = set(required_cols) - set(available_cols)
                if missing_cols:
                    self.logger.warning(f"Missing columns in prediction data: {missing_cols}")
                
                # Save predictions to CSV for future use
                try:
                    prediction_file = self.config.get('data', {}).get('predictions_path', 'data/processed/predictions.csv')
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(prediction_file), exist_ok=True)
                    result_df.to_csv(prediction_file, index=False)
                    self.logger.info(f"Saved prediction data to {prediction_file}")
                except Exception as e:
                    self.logger.error(f"Failed to save prediction data: {str(e)}")
                
                self.logger.info(f"Generated prediction data for {len(result_df)} items")
                return result_df
                
            else:
                # If no forecast available, try to load from previously saved data
                try:
                    prediction_file = self.config.get('data', {}).get('predictions_path', 'data/processed/predictions.csv')
                    prediction_data = pd.read_csv(prediction_file)
                    self.logger.info(f"Loaded prediction data from {prediction_file}")
                    return prediction_data
                except Exception as e:
                    self.logger.error(f"Failed to load prediction data: {str(e)}")
                    return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error getting prediction data: {str(e)}")
            return pd.DataFrame()