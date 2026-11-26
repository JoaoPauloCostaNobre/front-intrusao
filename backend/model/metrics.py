"""Medidas de avaliação (Seção 2.2.1 do TCC): matriz de confusão, precisão, revocação e F1."""
from __future__ import annotations

from sklearn.metrics import confusion_matrix, precision_recall_fscore_support


def avaliar(y_real, y_pred) -> dict:
    """Calcula as métricas com Ataque como positiva e com Normal como positiva."""
    vn, fp, fn, vp = confusion_matrix(y_real, y_pred, labels=[0, 1]).ravel()
    p, r, f, _ = precision_recall_fscore_support(y_real, y_pred, labels=[0, 1], zero_division=0)
    return {
        "matriz": {"VP": int(vp), "FP": int(fp), "VN": int(vn), "FN": int(fn)},
        "normal": {"precisao": float(p[0]), "revocacao": float(r[0]), "f1": float(f[0])},
        "ataque": {"precisao": float(p[1]), "revocacao": float(r[1]), "f1": float(f[1])},
    }


# Valores publicados por Vieira (2024, Tabelas 12 e 13) — linha de base
REFERENCIA_VIEIRA = {
    "terca": {
        "if": {"f1_ataque": 0.26, "normal": (0.96, 0.55, 0.70)},
        "lofn": {"f1_ataque": 0.22, "normal": (0.92, 0.83, 0.87)},
        "ocsvm": {"f1_ataque": 0.43, "normal": (0.95, 0.90, 0.92)},
        "lofs": {"f1_ataque": 0.17, "normal": (0.91, 0.76, 0.83)},
    },
    "sexta": {
        "if": {"f1_ataque": 0.50, "normal": (0.28, 0.56, 0.37)},
        "lofn": {"f1_ataque": 0.55, "normal": (0.38, 0.83, 0.52)},
        "ocsvm": {"f1_ataque": 0.32, "normal": (0.32, 0.90, 0.48)},
        "lofs": {"f1_ataque": 0.45, "normal": (0.32, 0.75, 0.45)},
    },
}
