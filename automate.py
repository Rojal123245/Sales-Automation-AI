#!/usr/bin/env python
"""
Standalone script for running the automation process.
This script can be scheduled with cron or other scheduling tools.
"""

import os
import argparse
import logging
from utils.helpers import ConfigHandler
from utils.logging_config import setup_logging
from models.evaluate import ModelEvaluator
from automation.order_manager import OrderManager
from automation.visualization import generate_report

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sales Automation AI - Automation Runner')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--report', action='store_true', help='Generate report after automation')
    parser.add_argument('--report-dir', default='reports', help='Directory to save reports')
    args = parser.parse_args()
    
    # Load and validate configuration
    config = ConfigHandler.load_config(args.config)
    ConfigHandler.validate_config(config)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Sales Automation AI - Automation Runner")
    
    try:
        # Get data with predictions
        logger.info("Loading prediction data")
        evaluator = ModelEvaluator(config)
        predicted_data = evaluator.get_prediction_data()
        
        if predicted_data is None or predicted_data.empty:
            logger.error("No prediction data available. Aborting automation.")
            return 1
        
        # Run the automation process
        logger.info("Starting automation process")
        order_manager = OrderManager(config)
        success, order_results = order_manager.run_ordering_process(predicted_data)
        
        # Generate report if requested
        if args.report:
            logger.info("Generating automation report")
            os.makedirs(args.report_dir, exist_ok=True)
            generate_report(config, args.report_dir)
        
        # Log completion status
        if success:
            logger.info("Automation process completed successfully")
            if order_results:
                logger.info(f"Placed {len(order_results)} orders")
            return 0
        else:
            logger.warning("Automation process completed with errors")
            return 1
            
    except Exception as e:
        logger.error(f"Error during automation: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 