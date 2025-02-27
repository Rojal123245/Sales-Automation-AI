import pandas as pd
from typing import List, Dict

class DataPreprocessor:
    def __init__(self, config: Dict):
        self.config = config
        self.numeric_cols = config['features']['numeric_cols']
        self.date_col = config['features']['date_col']
    
    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(self.config['data']['input_path'])
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._convert_types(df)
        df = self._handle_missing_values(df)
        df = self._create_features(df)
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.date_col] = pd.to_datetime(df[self.date_col])
        df[self.numeric_cols] = df[self.numeric_cols].apply(pd.to_numeric)
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.date_col] = pd.to_datetime(df[self.date_col])
        df[self.numeric_cols] = df[self.numeric_cols].apply(pd.to_numeric)
        return df
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Time features
        df['month'] = df[self.date_col].dt.month
        df['quarter'] = df[self.date_col].dt.quarter
        df['year'] = df[self.date_col].dt.year
        df['dayofweek'] = df[self.date_col].dt.dayofweek
        df['is_weekend'] = df['dayofweek'].isin([5,6]).astype(int)
        
        # Item features
        df['stock_ratio'] = df['Stock Left'] / df['Total Stock']
        df['price_bins'] = pd.qcut(df['Price'], q=5, labels=[1, 2, 3, 4, 5])
        df['price_bins'] = pd.to_numeric(df['price_bins'], errors='coerce')
        df['sales_ratio'] = df['Sales'] / df['Total Stock']
        
        # Rolling features
        for window in [7, 30]:
            df[f'sales_ma_{window}d'] = df.groupby('Item Name')['Sales'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean())
            df[f'revenue_ma_{window}d'] = df.groupby('Item Name')['Revenue'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean())
            df[f'stock_ma_{window}d'] = df.groupby('Item Name')['Stock Left'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean())
        
        # Interaction features
        df['price_stock_ratio'] = df['Price'] * df['stock_ratio']
        df['sales_price_ratio'] = df['Sales'] * df['Price']
        
        # Lag features
        df['sales_lag1'] = df.groupby('Item Name')['Sales'].shift(1)
        df['sales_lag7'] = df.groupby('Item Name')['Sales'].shift(7)
        
        return df.bfill()
    
    def save_processed_data(self, df: pd.DataFrame):
        df.to_csv(self.config['data']['output_path'], index=False)
        print(f"Processed data saved to {self.config['data']['output_path']}")

    