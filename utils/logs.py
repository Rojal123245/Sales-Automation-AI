import yaml
import logging
from pathlib import Path

def load_config(path: str) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(config: dict):
    logging.basicConfig(
        level=config['logging']['level'],
        filename=config['logging']['path']
    )