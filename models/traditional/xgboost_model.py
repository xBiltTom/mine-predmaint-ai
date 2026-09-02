"""
Modelo Tradicional 2: XGBoost Classifier.
"""
from typing import Optional, Dict, Any
import numpy as np
import joblib
from xgboost import XGBClassifier
from models.base_model import BasePredictiveModel

class XGBoostModel(BasePredictiveModel):
    def __init__(self, n_estimators: int = 150, max_depth: int = 6, learning_rate: float = 0.08,
                 subsample: float = 0.85, colsample_bytree: float = 0.85, random_state: int = 42):
        super().__init__(name="XGBoost Classifier", architecture_type="TRADICIONAL")
        self.hyperparameters = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "random_state": random_state
        }
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            eval_metric="logloss",
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "XGBoostModel":
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
