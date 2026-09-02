"""
Clase base abstracta para modelos predictivos de mantenimiento.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

class BasePredictiveModel(ABC):
    def __init__(self, name: str, architecture_type: str):
        self.name = name
        self.architecture_type = architecture_type  # 'TRADICIONAL' o 'HIBRIDO'
        self.model = None
        self.is_trained = False
        self.metrics: Dict[str, Any] = {}
        self.hyperparameters: Dict[str, Any] = {}

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BasePredictiveModel":
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def save(self, filepath: str):
        pass

    @abstractmethod
    def load(self, filepath: str):
        pass

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Calcula métricas exhaustivas de evaluación."""
        y_pred = self.predict(X_test)
        y_prob = self.predict_proba(X_test)
        
        # Probabilidad de clase 1 (Falla)
        prob_falla = y_prob[:, 1] if y_prob.ndim == 2 and y_prob.shape[1] > 1 else y_prob.ravel()

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        try:
            auc = float(roc_auc_score(y_test, prob_falla))
        except Exception:
            auc = 0.5

        cm = confusion_matrix(y_test, y_pred).tolist()

        self.metrics = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm
        }
        return self.metrics
