"""
Pruebas automatizadas de Modelos de IA, Evaluación y Pruebas Estadísticas.
"""
import pytest
import numpy as np
from models.traditional.random_forest import RandomForestModel
from models.traditional.xgboost_model import XGBoostModel
from models.traditional.svm_model import SVMModel
from models.hybrid.lstm_ae_rf import LSTMAERFModel
from models.statistical_tests import StatisticalComparator

@pytest.fixture
def dummy_data():
    np.random.seed(42)
    X = np.random.randn(100, 9)
    y = np.random.choice([0, 1], size=100, p=[0.85, 0.15])
    return X, y

def test_random_forest_training_and_evaluation(dummy_data):
    X, y = dummy_data
    rf = RandomForestModel(n_estimators=20, max_depth=4)
    rf.fit(X, y)
    metrics = rf.evaluate(X, y)
    assert rf.is_trained is True
    assert "accuracy" in metrics
    assert "roc_auc" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0

def test_xgboost_training_and_evaluation(dummy_data):
    X, y = dummy_data
    xgb = XGBoostModel(n_estimators=20, max_depth=3)
    xgb.fit(X, y)
    metrics = xgb.evaluate(X, y)
    assert xgb.is_trained is True
    assert "f1_score" in metrics

def test_svm_training_and_evaluation(dummy_data):
    X, y = dummy_data
    svm = SVMModel(C=1.0)
    svm.fit(X, y)
    metrics = svm.evaluate(X, y)
    assert svm.is_trained is True
    assert "precision" in metrics

def test_hybrid_lstm_ae_rf_training(dummy_data):
    X, y = dummy_data
    hybrid = LSTMAERFModel(seq_len=3, rf_trees=15)
    hybrid.fit(X, y)
    metrics = hybrid.evaluate(X, y)
    assert hybrid.is_trained is True
    assert "roc_auc" in metrics

def test_statistical_hypothesis_tests():
    scores_a = [0.952, 0.961, 0.945, 0.968, 0.954]
    scores_b = [0.884, 0.891, 0.875, 0.902, 0.880]
    res = StatisticalComparator.compare_models(scores_a, scores_b, alpha=0.05)
    assert "p_value_final" in res
    assert res["es_significativo"] is True
    assert "Wilcoxon" in res["prueba_recomendada"] or "t-Student" in res["prueba_recomendada"]
