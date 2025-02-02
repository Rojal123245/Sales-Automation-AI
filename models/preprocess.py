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
        df['month'] = df['Date'].dt.month
        df['quarter'] = df['Date'].dt.quarter
        df['year'] = df['Date'].dt.year
        df['dayofweek'] = df['Date'].dt.dayofweek
        df['is_weekend'] = df['dayofweek'].isin([5,6]).astype(int)
        return df
    
    def save_processed_data(self, df: pd.DataFrame):
        df.to_csv(self.config['data']['output_path'], index=False)
        print(f"Processed data saved to {self.config['data']['output_path']}")

    