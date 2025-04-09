import pandas as pd
from typing import List, Dict
import logging

class DataPreprocessor:
    def __init__(self, config: Dict):
        self.config = config
        self.numeric_cols = config['features']['numeric_cols']
        self.date_col = config['features']['date_col']
        self.logger = logging.getLogger(__name__)
    
    def load_data(self) -> pd.DataFrame:
        """Load data from the configured input path"""
        self.logger.info(f"Loading data from {self.config['data']['input_path']}")
        return pd.read_csv(self.config['data']['input_path'])
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the input dataframe with all preprocessing steps"""
        self.logger.info("Starting data preprocessing")
        df = self._convert_types(df)
        df = self._handle_missing_values(df)
        df = self._create_features(df)
        self.logger.info("Data preprocessing completed")
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert column types to appropriate data types"""
        self.logger.debug("Converting data types")
        df[self.date_col] = pd.to_datetime(df[self.date_col])
        df[self.numeric_cols] = df[self.numeric_cols].apply(pd.to_numeric, errors='coerce')
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        self.logger.debug("Handling missing values")
        # Log missing value statistics
        missing_stats = df[self.numeric_cols].isnull().sum()
        if missing_stats.any():
            self.logger.warning(f"Missing values found:\n{missing_stats[missing_stats > 0]}")
        
        df[self.numeric_cols] = df[self.numeric_cols].fillna(method='ffill').fillna(method='bfill')
        return df
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create all required features for the model"""
        self.logger.debug("Creating features")
        
        # Time-based features
        df['dayofweek'] = df[self.date_col].dt.dayofweek
        df['month'] = df[self.date_col].dt.month
        df['quarter'] = df[self.date_col].dt.quarter
        df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
        
        # Lag features
        df['sales_lag1'] = df['Sales'].shift(1)
        df['sales_lag7'] = df['Sales'].shift(7)
        
        # Moving averages
        df['sales_ma_7d'] = df['Sales'].rolling(window=7, min_periods=1).mean()
        df['sales_ma_14d'] = df['Sales'].rolling(window=14, min_periods=1).mean()
        df['sales_ma_30d'] = df['Sales'].rolling(window=30, min_periods=1).mean()
        df['sales_ma_90d'] = df['Sales'].rolling(window=90, min_periods=1).mean()
        
        # Seasonal decomposition features
        from statsmodels.tsa.seasonal import seasonal_decompose
        try:
            seasonal = seasonal_decompose(
                df.set_index(self.date_col)['Sales'],
                period=30,  # Assuming monthly seasonality
                extrapolate_trend='freq'
            )
            df['seasonal'] = seasonal.seasonal
            df['trend'] = seasonal.trend
            df['residual'] = seasonal.resid
        except Exception as e:
            self.logger.warning(f"Could not create seasonal decomposition features: {str(e)}")
        
        # Enhanced Item features
        df['stock_ratio'] = df['Stock Left'] / df['Total Stock'].replace(0, 1)
        df['price_bins'] = pd.qcut(df['Price'], q=5, labels=[1, 2, 3, 4, 5])
        df['price_bins'] = pd.to_numeric(df['price_bins'], errors='coerce')
        df['sales_ratio'] = df['Sales'] / df['Total Stock'].replace(0, 1)
        
        # Momentum features
        df['sales_momentum_7d'] = df['sales_ma_7d'] / df['sales_ma_30d'].replace(0, 1)
        df['sales_momentum_14d'] = df['sales_ma_14d'] / df['sales_ma_90d'].replace(0, 1)
        
        # Enhanced Interaction features
        df['price_stock_ratio'] = df['Price'] * df['stock_ratio']
        df['sales_price_ratio'] = df['Sales'] * df['Price']
        df['stock_price_interaction'] = df['Stock Left'] * df['Price']
        df['sales_stock_ratio'] = df['Sales'] / df['Stock Left'].replace(0, 1)
        
        self.logger.info(f"Created {len(df.columns)} features")
        return df.bfill()
    
    def save_processed_data(self, df: pd.DataFrame):
        """Save processed data to the configured output path"""
        output_path = self.config['data']['output_path']
        self.logger.info(f"Saving processed data to {output_path}")
        df.to_csv(output_path, index=False)
        self.logger.debug(f"Saved {len(df)} rows and {len(df.columns)} columns")

    
