import pandas as pd
from typing import List

class DataPreprocessor:
    def __init__(self, config: dict):
        self.numeric_cols = config['features']['numeric_cols']
        self.date_col = config['features']['date_col']
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._convert_types(df)
        df = self._create_features(df)
        return df