import pytest
import pandas as pd
from models import DataPreprocessor, ModelTrainer, ModelEvaluator

def test_preprocessor():
    sample_data = pd.DataFrame({
        'date': ['2024-01-01'],
        'sales': [100]
    })
    config = {'features': {'numeric_cols': ['sales'], 'date_col': 'date'}}
    preprocessor = DataPreprocessor(config)
    processed_data = preprocessor.process(sample_data)
    assert isinstance(processed_data, pd.DataFrame)