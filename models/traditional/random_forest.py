"""
Modelo Tradicional 1: Random Forest Classifier.
"""
from typing import Optional, Dict, Any
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from models.base_model import BasePredictiveModel

class RandomForestModel(BasePredictiveModel):
    def __init__(self, n_estimators: int = 150, max_depth: int = 12, min_samples_split: int = 4, random_state: int = 42):
        super().__init__(name="Random Forest Classifier", architecture_type="TRADICIONAL")
        self.hyperparameters = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "random_state": random_state
        }
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestModel":
        self.model.fit(X, y)
        self.is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def get_feature_importances(self) -> np.ndarray:
        if self.is_trained:
            return self.model.feature_importances_
        return np.array([])

    def save(self, filepath: str):
        joblib.dump({"model": self.model, "metrics": self.metrics, "hyperparams": self.hyperparameters}, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model = data["model"]
        self.metrics = data.get("metrics", {})
        self.hyperparameters = data.get("hyperparams", {})
        self.is_trained = True
