from statsmodels.tsa.arima.model import ARIMA

class ModelTrainer:
    def __init__(self, config: dict):
        self.order = config['model']['arima_params']['order']
    
    def train(self, data):
        model = ARIMA(data, order=self.order)
        return model.fit()