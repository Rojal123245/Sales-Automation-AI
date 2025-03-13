#!/usr/bin/env python3
"""
Script to download pre-trained models from external storage.
This is a placeholder script that should be customized for your specific storage solution.
"""

import os
import sys
import argparse
import requests
import yaml
from tqdm import tqdm

def load_config(config_path="config/config.yaml"):
    """Load configuration file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}

def download_file(url, destination):
    """
    Download a file from a URL with progress bar.
    
    Args:
        url: URL to download from
        destination: Local path to save the file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    try:
        # Stream the download to show progress
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB chunks
        
        print(f"Downloading from {url} to {destination}")
        
        with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(block_size):
                file.write(data)
                progress_bar.update(len(data))
                
        print(f"Download complete: {destination}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download pre-trained models")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--model-url", help="URL to download the model from (overrides config)")
    parser.add_argument("--output", help="Output path (overrides config)")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Get model path from config or command line
    model_path = args.output or config.get('model', {}).get('save_path', 'models/saved/sales_forecast.pkl')
    
    # This URL should be configured for your specific storage solution
    # Examples:
    # - S3: https://your-bucket.s3.amazonaws.com/models/sales_forecast.pkl
    # - GCP: https://storage.googleapis.com/your-bucket/models/sales_forecast.pkl
    # - Azure: https://your-account.blob.core.windows.net/your-container/models/sales_forecast.pkl
    model_url = args.model_url or config.get('model', {}).get('download_url', 'https://example.com/models/sales_forecast.pkl')
    
    # Download the model
    success = download_file(model_url, model_path)
    
    if success:
        print(f"Model successfully downloaded to {model_path}")
        return 0
    else:
        print("Failed to download model")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 