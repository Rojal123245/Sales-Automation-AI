import numpy as np
from sklearn.metrics import mean_squared_error

class ModelEvaluator:
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        return {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': np.mean(np.abs(y_true - y_pred))
        }