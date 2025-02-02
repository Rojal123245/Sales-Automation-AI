import yaml
import pandas as pd
from typing import List, Dict

class DataAnalyzer:
    def __init__(self, config: Dict):
        self.config = config

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(self.config['data']['input_path'])
    
    def describe_data(self) -> Dict:
        df = self.load_data()
        return {
            'summary': df.describe().to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'unique_items': df ['Item Name'].nunique()
        }
    

class ConfigHandler:
    @staticmethod
    def load_config(config_path: str = 'config/config.yaml') -> Dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
        

    @staticmethod
    def validate_config(config: Dict):
        required_sections = ['data', 'features', 'model']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Config file is missing {section} section")
            
    