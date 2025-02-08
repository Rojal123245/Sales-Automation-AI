from utils.helpers import ConfigHandler, DataAnalyzer
from models.preprocess import DataPreprocessor
from models.train import SalesForecastTrainer
from models.evaluate import ModelEvaluator

def main():

    config = ConfigHandler.load_config()
    ConfigHandler.validate_config(config)

    preprocessor = DataPreprocessor(config)
    raw_data = preprocessor.load_data()
    processed_data = preprocessor.process(raw_data)
    preprocessor.save_processed_data(processed_data)

    analyzer = DataAnalyzer(config)
    print(analyzer.describe_data())

    trainer = SalesForecastTrainer(config)
    model = trainer.full_pipeline()

    evaluator = ModelEvaluator(config)
    df = evaluator.load_data()
    evaluator.adf_test(df['Sales'])\
             .plot_sales_trend(df)\
             .plot_forecast(df)
    report = evaluator.generate_report()
    print("\nEvaluation Report:")
    print(report)


if __name__ == "__main__":
    main()