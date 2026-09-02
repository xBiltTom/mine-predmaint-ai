"""
Modelo Híbrido 1: CNN-LSTM (Redes Convolucionales 1D + LSTM).
Diseñado para extracción de firmas de vibración/presión en alta frecuencia y secuencias temporales.
Soporta aceleración GPU (CUDA) y CPU transparente.
"""
from typing import Optional, Dict, Any, Tuple
import numpy as np
import joblib
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
    class CNNLSTMNetwork(nn.Module):
        def __init__(self, input_dim: int = 9, conv_filters: int = 32, lstm_hidden: int = 48, dropout: float = 0.25):
            super().__init__()
            # Entrada esperada: (batch_size, input_dim, seq_len)
            self.conv1 = nn.Conv1d(in_channels=input_dim, out_channels=conv_filters, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.batchnorm = nn.BatchNorm1d(conv_filters)
            
            # LSTM espera (batch_size, seq_len, conv_filters)
            self.lstm = nn.LSTM(input_size=conv_filters, hidden_size=lstm_hidden, batch_first=True, bidirectional=False)
            self.dropout = nn.Dropout(dropout)
            self.fc1 = nn.Linear(lstm_hidden, 24)
            self.fc_out = nn.Linear(24, 2)  # 2 clases (Normal / Falla)

        def forward(self, x):
            # x shape: (batch_size, seq_len, input_dim) -> transponer a (batch_size, input_dim, seq_len)
            x = x.transpose(1, 2)
            c = self.conv1(x)
            c = self.relu(c)
            c = self.batchnorm(c)
            
            # volver a (batch_size, seq_len, conv_filters) para LSTM
            c = c.transpose(1, 2)
            lstm_out, (h_n, _) = self.lstm(c)
            last_hidden = lstm_out[:, -1, :]
            d = self.dropout(last_hidden)
            f = self.relu(self.fc1(d))
            out = self.fc_out(f)
            return out


class CNNLSTMModel(BasePredictiveModel):
    def __init__(self, seq_len: int = 5, epochs: int = 15, batch_size: int = 64, lr: float = 0.002):
        super().__init__(name="Híbrido CNN-LSTM", architecture_type="HIBRIDO")
        self.seq_len = seq_len
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.network = None
        self.fallback_model = None

    def _prepare_sequences(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Construye secuencias deslizantes temporales."""
        N, D = X.shape
        if N < self.seq_len:
            # Replicar para completar seq_len si es una sola muestra
            padded = np.tile(X, (self.seq_len, 1))
            return np.expand_dims(padded, axis=0), (np.array([y[-1]]) if y is not None else None)
        
        num_seqs = N - self.seq_len + 1
        seq_X = np.zeros((num_seqs, self.seq_len, D), dtype=np.float32)
        for i in range(num_seqs):
            seq_X[i] = X[i : i + self.seq_len]
        
        seq_y = y[self.seq_len - 1 :] if y is not None else None
        return seq_X, seq_y

    def fit(self, X: np.ndarray, y: np.ndarray) -> "CNNLSTMModel":
        if TORCH_AVAILABLE:
            seq_X, seq_y = self._prepare_sequences(X, y)
            tensor_x = torch.tensor(seq_X, dtype=torch.float32)
            tensor_y = torch.tensor(seq_y, dtype=torch.long)
            dataset = TensorDataset(tensor_x, tensor_y)
            loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

            input_dim = X.shape[1]
            self.network = CNNLSTMNetwork(input_dim=input_dim).to(self.device)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.network.parameters(), lr=self.lr, weight_decay=1e-4)

            self.network.train()
            for epoch in range(self.epochs):
                for b_x, b_y in loader:
                    b_x, b_y = b_x.to(self.device), b_y.to(self.device)
                    optimizer.zero_grad()
                    out = self.network(b_x)
                    loss = criterion(out, b_y)
                    loss.backward()
                    optimizer.step()
            self.is_trained = True
        else:
            # Fallback elegante usando MLPClassifier si PyTorch no está instalado localmente
            from sklearn.neural_network import MLPClassifier
            self.fallback_model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=self.epochs * 5, random_state=42)
            self.fallback_model.fit(X, y)
            self.is_trained = True

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        prob = self.predict_proba(X)
        return (prob[:, 1] >= 0.5).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if TORCH_AVAILABLE and self.network is not None:
            self.network.eval()
            seq_X, _ = self._prepare_sequences(X)
            tensor_x = torch.tensor(seq_X, dtype=torch.float32).to(self.device)
            with torch.no_grad():
                logits = self.network(tensor_x)
                probs = torch.softmax(logits, dim=1).cpu().numpy()
            
            # Si se generaron menos secuencias que N por el tamaño de ventana, alinear longitud
            if len(probs) < len(X):
                diff = len(X) - len(probs)
                first_row = np.tile(probs[0:1], (diff, 1))
                probs = np.vstack([first_row, probs])
            return probs
        elif self.fallback_model is not None:
            return self.fallback_model.predict_proba(X)
        else:
            raise RuntimeError("El modelo no ha sido entrenado.")

    def save(self, filepath: str):
        if TORCH_AVAILABLE and self.network is not None:
            torch.save({
                "state_dict": self.network.state_dict(),
                "metrics": self.metrics,
                "hyperparams": self.hyperparameters,
                "seq_len": self.seq_len
            }, filepath)
        elif self.fallback_model is not None:
            joblib.dump({"fallback": self.fallback_model, "metrics": self.metrics}, filepath)

    def load(self, filepath: str):
        if TORCH_AVAILABLE and self.network is not None:
            checkpoint = torch.load(filepath, map_location=self.device)
            self.network.load_state_dict(checkpoint["state_dict"])
            self.metrics = checkpoint.get("metrics", {})
            self.is_trained = True
        else:
            data = joblib.load(filepath)
            self.fallback_model = data["fallback"]
            self.metrics = data.get("metrics", {})
            self.is_trained = True
