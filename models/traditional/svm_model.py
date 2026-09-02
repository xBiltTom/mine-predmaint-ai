"""
Modelo Tradicional 3: Support Vector Machine (SVM) con Kernel RBF.
"""
from typing import Optional, Dict, Any
import numpy as np
import joblib
from sklearn.svm import SVC
from models.base_model import BasePredictiveModel

class SVMModel(BasePredictiveModel):
    def __init__(self, C: float = 2.0, kernel: str = "rbf", gamma: str = "scale", random_state: int = 42):
        super().__init__(name="Support Vector Machine (SVM RBF)", architecture_type="TRADICIONAL")
        self.hyperparameters = {
            "C": C,
            "kernel": kernel,
            "gamma": gamma,
            "probability": True,
            "random_state": random_state
        }
        self.model = SVC(
            C=C,
            kernel=kernel,
            gamma=gamma,
            probability=True,
            random_state=random_state,
            cache_size=500
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SVMModel":
        # Entrenar SVM con probabilidades calibradas
        self.model.fit(X, y)
        self.is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "metrics": self.metrics, "hyperparams": self.hyperparameters}, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model = data["model"]
        self.metrics = data.get("metrics", {})
        self.hyperparameters = data.get("hyperparams", {})
        self.is_trained = True
