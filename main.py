from utils.helpers import ConfigHandler, DataAnalyzer
from utils.logging_config import setup_logging
from models.preprocess import DataPreprocessor
from models.train import SalesForecastTrainer
from models.evaluate import ModelEvaluator
from automation.order_manager import OrderManager
import argparse
import logging

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Sales Automation AI')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--mode', choices=['train', 'predict', 'automate', 'full'], default='full',
                        help='Operation mode: train, predict, automate, or full pipeline')
    args = parser.parse_args()

    # Load and validate configuration
    config = ConfigHandler.load_config(args.config)
    ConfigHandler.validate_config(config)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Sales Automation AI in {args.mode} mode")

    if args.mode in ['train', 'full']:
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

    if args.mode in ['predict', 'automate', 'full']:
        # Model evaluation and prediction
        logger.info("Evaluating model and generating predictions")
        evaluator = ModelEvaluator(config)
        data = evaluator.load_data()
        evaluator.adf_test(data['Sales']).\
                plot_sales_trend(data).\
                plot_forecast(data, model)
        report = evaluator.generate_report()
        logger.info(f"Evaluation complete: RMSE={report.get('rmse', 'N/A')}")
        
        # Get data with predictions for automation
        predicted_data = evaluator.get_prediction_data()

    if args.mode in ['automate', 'full']:
        # Run the automation process
        logger.info("Starting automation process")
        order_manager = OrderManager(config)
        
        if 'predicted_data' not in locals():
            logger.warning("No prediction data available. Loading from file...")
            evaluator = ModelEvaluator(config)
            predicted_data = evaluator.get_prediction_data()
        
        if predicted_data is not None and not predicted_data.empty:
            success, order_results = order_manager.run_ordering_process(predicted_data)
            
            if success:
                logger.info("Automation process completed successfully")
                if order_results:
                    logger.info(f"Placed {len(order_results)} orders")
            else:
                logger.warning("Automation process completed with errors")
        else:
            logger.error("No prediction data available for automation")

    logger.info("Sales Automation AI execution complete")

if __name__ == "__main__":
    main()