"""
Módulo de Evaluación y Validación Cruzada (CRISP-DM Fase 5).
Implementa Stratified K-Fold (5 Folds), cálculo de curvas ROC/PR y matrices de confusión.
"""
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve, precision_recall_curve, confusion_matrix
from imblearn.over_sampling import SMOTE

class ModelEvaluator:
    @staticmethod
    def evaluate_model_cv(model_class, model_kwargs: dict, X: np.ndarray, y: np.ndarray, n_splits: int = 5, random_state: int = 42) -> Dict[str, Any]:
        """
        Ejecuta validación cruzada estratificada con SMOTE aplicado solo en train.
        Retorna métricas promedio, desviación estándar y los scores por cada fold
        (indispensables para los tests estadísticos).
        """
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        
        fold_metrics = {
            "accuracy": [],
            "precision": [],
            "recall": [],
            "f1_score": [],
            "roc_auc": []
        }
        
        y_true_all = []
        y_prob_all = []

        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train_f, y_train_f = X[train_idx], y[train_idx]
            X_val_f, y_val_f = X[val_idx], y[val_idx]

            # SMOTE en el fold de entrenamiento
            smote = SMOTE(random_state=random_state + fold)
            X_train_res, y_train_res = smote.fit_resample(X_train_f, y_train_f)

            # Instanciar y entrenar modelo
            inst = model_class(**model_kwargs)
            inst.fit(X_train_res, y_train_res)

            # Inferencia en validación
            preds = inst.predict(X_val_f)
            probs = inst.predict_proba(X_val_f)
            prob_falla = probs[:, 1] if probs.ndim == 2 and probs.shape[1] > 1 else probs.ravel()

            fold_metrics["accuracy"].append(float(accuracy_score(y_val_f, preds)))
            fold_metrics["precision"].append(float(precision_score(y_val_f, preds, zero_division=0)))
            fold_metrics["recall"].append(float(recall_score(y_val_f, preds, zero_division=0)))
            fold_metrics["f1_score"].append(float(f1_score(y_val_f, preds, zero_division=0)))
            try:
                auc_val = float(roc_auc_score(y_val_f, prob_falla))
            except Exception:
                auc_val = 0.5
            fold_metrics["roc_auc"].append(auc_val)

            y_true_all.extend(y_val_f.tolist())
            y_prob_all.extend(prob_falla.tolist())

        summary = {
            metric: {
                "mean": round(float(np.mean(vals)), 4),
                "std": round(float(np.std(vals)), 4),
                "folds": [round(v, 4) for v in vals]
            }
            for metric, vals in fold_metrics.items()
        }

        # Curvas ROC y PR globales
        fpr, tpr, _ = roc_curve(y_true_all, y_prob_all)
        precision_curve, recall_curve, _ = precision_recall_curve(y_true_all, y_prob_all)

        return {
            "summary": summary,
            "raw_folds": fold_metrics,
            "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
            "pr_curve": {"precision": precision_curve.tolist(), "recall": recall_curve.tolist()}
        }
