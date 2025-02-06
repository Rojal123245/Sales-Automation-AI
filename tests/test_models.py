import pytest
import pandas as pd
from models import DataPreprocessor, ModelEvaluator

def test_preprocessor():
    sample_data = pd.DataFrame({
        'Date': ['2024-01-01'],
        'sales': [100]
    })
    config = {'features': {'numeric_cols': ['sales'], 'date_col': 'Date'}}
    preprocessor = DataPreprocessor(config)
    processed_data = preprocessor.process(sample_data)
    assert isinstance(processed_data, pd.DataFrame) 