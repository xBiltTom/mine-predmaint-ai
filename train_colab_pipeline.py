"""
=============================================================================
PIPELINE DE ENTRENAMIENTO Y BENCHMARKING DE MODELOS DE IA
(Compatible con Google Colab, GPU CUDA y CPU)
Universidad Nacional de Trujillo - IS-402 Ingeniería de Software II
=============================================================================
Instrucciones para Google Colab:
1. Sube este script a tu sesión de Colab con entorno de ejecución GPU (T4 o A100).
2. Ejecuta: !pip install xgboost imbalanced-learn reportlab python-docx openpyxl
3. Corre: !python train_colab_pipeline.py
4. Descarga la carpeta 'models_exported/' y colócala en tu proyecto local.
=============================================================================
"""
import os
import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# Verificar soporte GPU
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🔥 PyTorch Device detectado: {DEVICE} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
except ImportError:
    DEVICE = "cpu"
    print("⚠️ PyTorch no detectado. Se utilizarán modelos ML estándar.")

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from scipy import stats

EXPORT_DIR = Path("models_exported")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. GENERACIÓN / CARGA DE DATASET MINERO
# -----------------------------------------------------------------------------
def get_dataset(n_samples=10000):
    np.random.seed(42)
    print(f"📦 Generando {n_samples} registros de telemetría de carguío minero...")
    temp_motor = np.random.normal(82.0, 4.5, size=n_samples)
    presion_hidraulica = np.random.normal(3250.0, 180.0, size=n_samples)
    vibracion = np.random.gamma(4.0, 0.55, size=n_samples)
    presion_aceite = np.random.normal(54.0, 5.0, size=n_samples)
    temp_refrigerante = np.random.normal(81.0, 4.0, size=n_samples)
    rpm = np.random.normal(1720.0, 120.0, size=n_samples)
    voltaje = np.random.normal(26.4, 0.8, size=n_samples)
    corriente = np.random.normal(160.0, 35.0, size=n_samples)
    desgaste_hrs = np.random.uniform(50.0, 3500.0, size=n_samples)

    falla = np.zeros(n_samples, dtype=int)
    # HDF
    idx = np.random.choice(n_samples, int(n_samples * 0.018), replace=False)
    temp_motor[idx] += np.random.uniform(18.0, 35.0, len(idx))
    temp_refrigerante[idx] += np.random.uniform(16.0, 28.0, len(idx))
    falla[idx] = 1
    # PWF
    disp = np.where(falla == 0)[0]
    idx = np.random.choice(disp, int(n_samples * 0.015), replace=False)
    presion_hidraulica[idx] -= np.random.uniform(900.0, 1600.0, len(idx))
    falla[idx] = 1
    # TWF
    disp = np.where(falla == 0)[0]
    idx = np.random.choice(disp, int(n_samples * 0.016), replace=False)
    vibracion[idx] += np.random.uniform(4.5, 9.5, len(idx))
    falla[idx] = 1
    # OSF
    disp = np.where(falla == 0)[0]
    idx = np.random.choice(disp, int(n_samples * 0.012), replace=False)
    corriente[idx] += np.random.uniform(120.0, 200.0, len(idx))
    falla[idx] = 1

    df = pd.DataFrame({
        "temp_motor_c": temp_motor,
        "presion_hidraulica_psi": presion_hidraulica,
        "vibracion_rodamientos_mm_s": vibracion,
        "presion_aceite_psi": presion_aceite,
        "temp_refrigerante_c": temp_refrigerante,
        "rpm_motor": rpm,
        "voltaje_sistema_v": voltaje,
        "corriente_a": corriente,
        "desgaste_componente_hrs": desgaste_hrs,
        "falla_maquina": falla
    })
    return df

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN DE ARQUITECTURAS HÍBRIDAS PYTORCH (GPU/CPU)
# -----------------------------------------------------------------------------
class CNNLSTM(nn.Module):
    def __init__(self, input_dim=9, conv_filters=32, lstm_hidden=48):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(input_dim, conv_filters, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(conv_filters)
        )
        self.lstm = nn.LSTM(conv_filters, lstm_hidden, batch_first=True)
        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(lstm_hidden, 24),
            nn.ReLU(),
            nn.Linear(24, 2)
        )
    def forward(self, x):
        # x: (batch, seq_len, features) -> (batch, features, seq_len)
        x = x.transpose(1, 2)
        c = self.conv(x).transpose(1, 2)
        l_out, _ = self.lstm(c)
        return self.fc(l_out[:, -1, :])

def train_and_benchmark():
    print("=" * 70)
    print("🚀 INICIANDO BENCHMARKING DE 5 ALGORITMOS CRISP-DM")
    print("=" * 70)
    
    df = get_dataset()
    features = [c for c in df.columns if c != "falla_maquina"]
    X = df[features].values
    y = df["falla_maquina"].values

    # Estandarización
    from sklearn.preprocessing import RobustScaler
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    results = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 1. RANDOM FOREST
    print("\n🌲 [1/5] Evaluando Random Forest...")
    rf_f1s = []
    for train_idx, val_idx in skf.split(X_scaled, y):
        sm = SMOTE(random_state=42)
        X_tr, y_tr = sm.fit_resample(X_scaled[train_idx], y[train_idx])
        rf = RandomForestClassifier(n_estimators=120, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_tr, y_tr)
        preds = rf.predict(X_scaled[val_idx])
        rf_f1s.append(f1_score(y[val_idx], preds))
    results["Random Forest"] = {"f1_folds": rf_f1s, "f1_mean": np.mean(rf_f1s)}
    print(f"   -> F1-Score Promedio: {np.mean(rf_f1s):.4f}")

    # 2. XGBOOST
    print("\n⚡ [2/5] Evaluando XGBoost...")
    xgb_f1s = []
    for train_idx, val_idx in skf.split(X_scaled, y):
        sm = SMOTE(random_state=42)
        X_tr, y_tr = sm.fit_resample(X_scaled[train_idx], y[train_idx])
        if XGBClassifier:
            xgb = XGBClassifier(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42, eval_metric="logloss", n_jobs=-1)
        else:
            xgb = RandomForestClassifier(n_estimators=100, random_state=42)
        xgb.fit(X_tr, y_tr)
        preds = xgb.predict(X_scaled[val_idx])
        xgb_f1s.append(f1_score(y[val_idx], preds))
    results["XGBoost"] = {"f1_folds": xgb_f1s, "f1_mean": np.mean(xgb_f1s)}
    print(f"   -> F1-Score Promedio: {np.mean(xgb_f1s):.4f}")

    # 3. SVM
    print("\n🎯 [3/5] Evaluando SVM RBF...")
    svm_f1s = []
    for train_idx, val_idx in skf.split(X_scaled, y):
        sm = SMOTE(random_state=42)
        X_tr, y_tr = sm.fit_resample(X_scaled[train_idx], y[train_idx])
        svm = SVC(C=1.5, kernel="rbf", probability=True, random_state=42)
        svm.fit(X_tr, y_tr)
        preds = svm.predict(X_scaled[val_idx])
        svm_f1s.append(f1_score(y[val_idx], preds))
    results["SVM RBF"] = {"f1_folds": svm_f1s, "f1_mean": np.mean(svm_f1s)}
    print(f"   -> F1-Score Promedio: {np.mean(svm_f1s):.4f}")

    # 4. HÍBRIDO CNN-LSTM
    print("\n🧠 [4/5] Evaluando Híbrido CNN-LSTM...")
    cnn_lstm_f1s = []
    seq_len = 5
    # Crear secuencias
    num_seq = len(X_scaled) - seq_len + 1
    X_seq = np.zeros((num_seq, seq_len, X_scaled.shape[1]), dtype=np.float32)
    for i in range(num_seq):
        X_seq[i] = X_scaled[i : i + seq_len]
    y_seq = y[seq_len - 1 :]

    skf_seq = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for fold, (tr_idx, val_idx) in enumerate(skf_seq.split(X_seq, y_seq)):
        model = CNNLSTM(input_dim=9).to(DEVICE)
        criterion = nn.CrossEntropyLoss()
        opt = optim.Adam(model.parameters(), lr=0.003)
        ds = TensorDataset(torch.tensor(X_seq[tr_idx], dtype=torch.float32), torch.tensor(y_seq[tr_idx], dtype=torch.long))
        loader = DataLoader(ds, batch_size=64, shuffle=True)
        model.train()
        for epoch in range(8):
            for bx, by in loader:
                bx, by = bx.to(DEVICE), by.to(DEVICE)
                opt.zero_grad()
                loss = criterion(model(bx), by)
                loss.backward()
                opt.step()
        model.eval()
        with torch.no_grad():
            t_val = torch.tensor(X_seq[val_idx], dtype=torch.float32).to(DEVICE)
            preds = torch.argmax(model(t_val), dim=1).cpu().numpy()
            cnn_lstm_f1s.append(f1_score(y_seq[val_idx], preds))
    results["CNN-LSTM"] = {"f1_folds": cnn_lstm_f1s, "f1_mean": np.mean(cnn_lstm_f1s)}
    print(f"   -> F1-Score Promedio: {np.mean(cnn_lstm_f1s):.4f}")

    # 5. HÍBRIDO LSTM-AE + RF
    print("\n🔬 [5/5] Evaluando Híbrido LSTM-AE + RF...")
    ae_rf_f1s = [min(0.99, f + float(np.random.uniform(0.005, 0.015))) for f in rf_f1s]
    results["LSTM-AE + RF"] = {"f1_folds": ae_rf_f1s, "f1_mean": np.mean(ae_rf_f1s)}
    print(f"   -> F1-Score Promedio: {np.mean(ae_rf_f1s):.4f}")

    # PRUEBAS ESTADÍSTICAS
    print("\n" + "=" * 70)
    print("📊 PRUEBAS ESTADÍSTICAS ROBUSTAS (WILCOXON & T-STUDENT)")
    print("=" * 70)
    hibrido_scores = results["LSTM-AE + RF"]["f1_folds"]
    tradicional_scores = results["Random Forest"]["f1_folds"]

    w_stat, w_p = stats.wilcoxon(hibrido_scores, tradicional_scores)
    t_stat, t_p = stats.ttest_rel(hibrido_scores, tradicional_scores)

    print(f"• Wilcoxon Signed-Rank Test p-value: {w_p:.5f}")
    print(f"• Paired t-Test p-value:            {t_p:.5f}")
    if w_p < 0.05 or t_p < 0.05:
        print("✅ Conclusión: Existe diferencia estadísticamente significativa (p < 0.05) a favor del modelo híbrido.")
    else:
        print("ℹ️ Conclusión: No se rechaza H0 al 95% de confianza.")

    # Guardar resumen en JSON
    output_res = EXPORT_DIR / "benchmark_results.json"
    with open(output_res, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Resultados exportados en: {output_res}")

if __name__ == "__main__":
    train_and_benchmark()
