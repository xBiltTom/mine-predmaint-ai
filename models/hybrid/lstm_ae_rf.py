"""
Modelo Híbrido 2: LSTM-Autoencoder + Random Forest.
El Autoencoder extrae representaciones latentes no lineales y error de reconstrucción (anomalía),
y un Random Forest clasifica el riesgo final de mantenimiento predictivo.
"""
from typing import Optional, Dict, Any, Tuple
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from models.base_model import BasePredictiveModel

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class LSTMAutoencoder(nn.Module):
        def __init__(self, input_dim: int, latent_dim: int = 16, hidden_dim: int = 32):
            super().__init__()
            # Encoder
            self.encoder_lstm1 = nn.LSTM(input_size=input_dim, hidden_size=hidden_dim, batch_first=True)
            self.encoder_lstm2 = nn.LSTM(input_size=hidden_dim, hidden_size=latent_dim, batch_first=True)
            
            # Decoder
            self.decoder_lstm1 = nn.LSTM(input_size=latent_dim, hidden_size=hidden_dim, batch_first=True)
            self.decoder_out = nn.Linear(hidden_dim, input_dim)

        def encode(self, x):
            out, _ = self.encoder_lstm1(x)
            out, (h_n, _) = self.encoder_lstm2(out)
            return h_n[-1]  # Espacio latente del último estado

        def forward(self, x):
            batch_size, seq_len, _ = x.shape
            latent = self.encode(x)
            # Repetir vector latente a través del tiempo
            rep = latent.unsqueeze(1).repeat(1, seq_len, 1)
            dec_out, _ = self.decoder_lstm1(rep)
            reconstructed = self.decoder_out(dec_out)
            return reconstructed, latent


class LSTMAERFModel(BasePredictiveModel):
    def __init__(self, seq_len: int = 5, latent_dim: int = 16, epochs: int = 15, rf_trees: int = 100):
        super().__init__(name="Híbrido LSTM-Autoencoder + RF", architecture_type="HIBRIDO")
        self.seq_len = seq_len
        self.latent_dim = latent_dim
        self.epochs = epochs
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.autoencoder = None
        self.rf_classifier = RandomForestClassifier(n_estimators=rf_trees, max_depth=10, random_state=42, n_jobs=-1)
        self.pca_fallback = None

    def _prepare_sequences(self, X: np.ndarray) -> np.ndarray:
        N, D = X.shape
        if N < self.seq_len:
            padded = np.tile(X, (self.seq_len, 1))
            return np.expand_dims(padded, axis=0)
        num_seqs = N - self.seq_len + 1
        seq_X = np.zeros((num_seqs, self.seq_len, D), dtype=np.float32)
        for i in range(num_seqs):
            seq_X[i] = X[i : i + self.seq_len]
        return seq_X

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LSTMAERFModel":
        if TORCH_AVAILABLE:
            # 1. Entrenar Autoencoder en datos normales (y == 0) para reconstrucción
            normal_mask = (y == 0)
            X_normal = X[normal_mask] if np.sum(normal_mask) > 10 else X
            seq_X_normal = self._prepare_sequences(X_normal)
            
            input_dim = X.shape[1]
            self.autoencoder = LSTMAutoencoder(input_dim=input_dim, latent_dim=self.latent_dim).to(self.device)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.autoencoder.parameters(), lr=0.003)

            dataset = TensorDataset(torch.tensor(seq_X_normal, dtype=torch.float32))
            loader = DataLoader(dataset, batch_size=64, shuffle=True)

            self.autoencoder.train()
            for epoch in range(self.epochs):
                for (b_x,) in loader:
                    b_x = b_x.to(self.device)
                    optimizer.zero_grad()
                    recon, _ = self.autoencoder(b_x)
                    loss = criterion(recon, b_x)
                    loss.backward()
                    optimizer.step()

            # 2. Extraer características latentes + error de reconstrucción para todo el dataset
            latent_features = self._extract_features(X)
            # Alinear tamaño de y
            y_aligned = y[-len(latent_features):]
            self.rf_classifier.fit(latent_features, y_aligned)
            self.is_trained = True
        else:
            # Fallback elegante usando PCA + Reconstruction Error + Random Forest
            self.pca_fallback = PCA(n_components=min(5, X.shape[1]))
            latent = self.pca_fallback.fit_transform(X)
            recon = self.pca_fallback.inverse_transform(latent)
            recon_error = np.mean((X - recon) ** 2, axis=1, keepdims=True)
            combined_features = np.hstack([X, latent, recon_error])
            self.rf_classifier.fit(combined_features, y)
            self.is_trained = True

        return self

    def _extract_features(self, X: np.ndarray) -> np.ndarray:
        if TORCH_AVAILABLE and self.autoencoder is not None:
            self.autoencoder.eval()
            seq_X = self._prepare_sequences(X)
            tensor_x = torch.tensor(seq_X, dtype=torch.float32).to(self.device)
            with torch.no_grad():
                recon, latent = self.autoencoder(tensor_x)
                # Error de reconstrucción MAE
                rec_error = torch.mean(torch.abs(recon - tensor_x), dim=(1, 2)).unsqueeze(1)
                combined = torch.cat([latent, rec_error], dim=1).cpu().numpy()
            return combined
        elif self.pca_fallback is not None:
            latent = self.pca_fallback.transform(X)
            recon = self.pca_fallback.inverse_transform(latent)
            rec_error = np.mean((X - recon) ** 2, axis=1, keepdims=True)
            return np.hstack([X, latent, rec_error])
        return X

    def predict(self, X: np.ndarray) -> np.ndarray:
        prob = self.predict_proba(X)
        return (prob[:, 1] >= 0.5).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        features = self._extract_features(X)
        probs = self.rf_classifier.predict_proba(features)
        if len(probs) < len(X):
            diff = len(X) - len(probs)
            first_row = np.tile(probs[0:1], (diff, 1))
            probs = np.vstack([first_row, probs])
        return probs

    def save(self, filepath: str):
        payload = {
            "rf": self.rf_classifier,
            "metrics": self.metrics,
            "pca_fallback": self.pca_fallback
        }
        if TORCH_AVAILABLE and self.autoencoder is not None:
            payload["autoencoder_state"] = self.autoencoder.state_dict()
        joblib.dump(payload, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.rf_classifier = data["rf"]
        self.metrics = data.get("metrics", {})
        self.pca_fallback = data.get("pca_fallback")
        if TORCH_AVAILABLE and "autoencoder_state" in data:
            self.autoencoder = LSTMAutoencoder(input_dim=9, latent_dim=self.latent_dim).to(self.device)
            self.autoencoder.load_state_dict(data["autoencoder_state"])
        self.is_trained = True
