"""
Módulo de Preparación de Datos (CRISP-DM Fase 3).
Limpieza, escalado robusto, ventanas temporales y rebalanceo de clases con SMOTE.
"""
from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from imblearn.over_sampling import SMOTE

FEATURE_COLS = [
    "temp_motor_c",
    "presion_hidraulica_psi",
    "vibracion_rodamientos_mm_s",
    "presion_aceite_psi",
    "temp_refrigerante_c",
    "rpm_motor",
    "voltaje_sistema_v",
    "corriente_a",
    "desgaste_componente_hrs"
]

TARGET_COL = "falla_maquina"
MULTICLASS_TARGET_COL = "tipo_falla"

class DataPreprocessor:
    def __init__(self, scaler_type: str = "robust"):
        self.scaler_type = scaler_type
        self.scaler = RobustScaler() if scaler_type == "robust" else StandardScaler()
        self.feature_names = FEATURE_COLS

    def prepare_train_test(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        apply_smote: bool = True,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Divide en train y test estratificado, escala y aplica SMOTE únicamente al train
        para garantizar rigor científico sin data leakage.
        """
        X = df[self.feature_names].values
        y = df[TARGET_COL].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Ajustar escalador en X_train y transformar ambos
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        if apply_smote:
            smote = SMOTE(random_state=random_state)
            X_train_final, y_train_final = smote.fit_resample(X_train_scaled, y_train)
        else:
            X_train_final, y_train_final = X_train_scaled, y_train

        return X_train_final, X_test_scaled, y_train_final, y_test

    def transform_single(self, sample_dict: dict) -> np.ndarray:
        """Transforma una muestra puntual para inferencia."""
        values = [sample_dict[col] for col in self.feature_names]
        arr = np.array(values).reshape(1, -1)
        return self.scaler.transform(arr)

    @staticmethod
    def create_sliding_sequences(X: np.ndarray, y: Optional[np.ndarray] = None, time_steps: int = 5) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Construye ventanas secuenciales tridimensionales (muestras, timesteps, features)
        para modelos de series temporales (CNN-LSTM, LSTM-Autoencoder).
        """
        num_samples = len(X) - time_steps + 1
        if num_samples <= 0:
            raise ValueError(f"Longitud de datos {len(X)} insuficiente para time_steps={time_steps}")
        
        num_features = X.shape[1]
        seq_X = np.zeros((num_samples, time_steps, num_features), dtype=np.float32)
        
        for i in range(num_samples):
            seq_X[i] = X[i : i + time_steps]
            
        if y is not None:
            seq_y = y[time_steps - 1 :]
            return seq_X, seq_y
            
        return seq_X, None
