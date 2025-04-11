from utils.helpers import ConfigHandler, DataAnalyzer
from utils.logging_config import setup_logging
from models.preprocess import DataPreprocessor
from models.train import SalesForecastTrainer
from models.evaluate import ModelEvaluator
import argparse
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
import json
from automation.inventory_manager import InventoryManager

def setup_environment():
    """Setup necessary directories and environment"""
    dirs = ['logs', 'data/processed', 'models/saved', 'reports']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def handle_training(config, logger):
    """Handle the training pipeline"""
    try:
        # Data preprocessing
        logger.info("Starting data preprocessing")
        preprocessor = DataPreprocessor(config)
        raw_data = preprocessor.load_data()
        processed_data = preprocessor.process(raw_data)
        preprocessor.save_processed_data(processed_data)

        # Data analysis
        logger.info("Analyzing data")
        analyzer = DataAnalyzer(config)
        analysis_results = analyzer.describe_data()
        logger.info(f"Data analysis complete: {len(analysis_results['summary'])} metrics calculated")

        # Model training
        logger.info("Training sales forecast model")
        trainer = SalesForecastTrainer(config)
        model = trainer.full_pipeline()
        logger.info("Model training complete")
        
        return model
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def handle_prediction(config, logger, model=None):
    """Handle the prediction pipeline"""
    try:
        logger.info("Evaluating model and generating predictions")
        evaluator = ModelEvaluator(config)
        data = evaluator.load_data()
        
        # Run statistical tests and generate plots
        evaluator.adf_test(data['Sales'])
        evaluator.plot_sales_trend(data)
        evaluator.plot_forecast(data, model)
        
        # Generate report
        report = evaluator.generate_report()
        logger.info(f"Evaluation complete: RMSE={report.get('performance_metrics', {}).get('rmse', 'N/A')}")
        
        # Get prediction data
        predicted_data = evaluator.get_prediction_data()
        
        # Save report to file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = Path(f"reports/evaluation_report_{timestamp}.json")
            
            # Ensure the reports directory exists
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert any numpy values to Python native types for JSON serialization
            def convert_to_native_types(obj):
                if hasattr(obj, 'item'):  # Handle numpy scalars
                    return obj.item()
                elif isinstance(obj, (list, tuple)):
                    return [convert_to_native_types(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: convert_to_native_types(v) for k, v in obj.items()}
                return obj
            
            report = convert_to_native_types(report)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
            logger.info(f"Evaluation report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save evaluation report: {str(e)}")
        
        # After generating predictions, handle automated ordering
        if not predicted_data.empty:
            logger.info("Processing predictions for automated ordering")
            inventory_manager = InventoryManager(config)
            
            # Update product cache first
            inventory_manager.update_product_cache()
            
            # Process orders
            order_result = inventory_manager.execute_orders(config['data']['predictions_path'])
            
            if order_result['status'] == 'success':
                logger.info(
                    f"Orders processed successfully. "
                    f"Items ordered: {order_result.get('items_ordered', 0)}, "
                    f"Total cost: ${order_result.get('total_cost', 0):.2f}"
                )
                if order_result.get('report_path'):
                    logger.info(f"Order report generated: {order_result['report_path']}")
            else:
                logger.error(f"Order processing failed: {order_result.get('message')}")
        else:
            logger.warning("No prediction data available for automated ordering")
        
        return predicted_data
    except Exception as e:
        logger.error(f"Prediction pipeline failed: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def main():
    try:
        # Setup environment
        setup_environment()
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Sales Automation AI')
        parser.add_argument('--config', default='config/config.yaml', 
                          help='Path to config file')
        parser.add_argument('--mode', 
                          choices=['train', 'predict', 'full'], 
                          default='full',
                          help='Operation mode: train, predict, or full pipeline')
        parser.add_argument('--debug', action='store_true', 
                          help='Enable debug logging')
        args = parser.parse_args()

        # Load and validate configuration
        config = ConfigHandler.load_config(args.config)
        ConfigHandler.validate_config(config)
        
        # Update logging level if debug flag is set
        if args.debug:
            config['logging']['level'] = 'DEBUG'
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting Sales Automation AI in {args.mode} mode")
        
        model = None
        predicted_data = None

        # Execute pipeline based on mode
        if args.mode in ['train', 'full']:
            model = handle_training(config, logger)
            if model is None and args.mode == 'train':
                sys.exit(1)

        if args.mode in ['predict', 'full']:
            predicted_data = handle_prediction(config, logger, model)
            if predicted_data is None and args.mode == 'predict':
                sys.exit(1)

        logger.info("Sales Automation AI execution complete")
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
