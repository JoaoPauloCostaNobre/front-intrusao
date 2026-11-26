"""Algoritmos de detecção de outliers usados por Vieira (2024).

Todos seguem a mesma interface:
    det = criar_detector(nome); det.fit(X_treino); pred = det.predict(X_teste)
onde pred = 1 para Ataque (outlier) e 0 para Normal.

Como em Vieira (2024), os algoritmos em lote usam os parâmetros padrão do scikit-learn.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

NOMES = {
    "if": "Isolation Forest",
    "lofn": "LOF - Novelty",
    "ocsvm": "SVM - One-Class",
    "lofs": "LOF - Stream",
}


class _Sklearn:
    """Adapta a saída do scikit-learn (+1 normal / -1 outlier) para 0/1."""

    def __init__(self, modelo):
        self.modelo = modelo

    def fit(self, X):
        self.modelo.fit(X)
        return self

    def predict(self, X):
        return (self.modelo.predict(X) == -1).astype(int)


class LOFStream:
    """LOF em fluxo contínuo com janela de referência.

    Reproduz a ideia usada por Vieira (2024) via PySAD/PyOD: o modelo inicial é
    treinado com as primeiras `n_inicial` instâncias de treino (100 no trabalho
    dela); as instâncias de teste chegam em sequência, são classificadas pelo
    modelo atual e entram numa janela deslizante que, a cada `passo` instâncias,
    serve para retreinar o LOF.

    Observação para o texto do TCC: Vieira (2024) não informa o tamanho da janela
    nem o limiar usado; aqui o limiar é o padrão do LOF do scikit-learn e a janela
    é um parâmetro. Documente os valores usados.
    """

    def __init__(self, n_inicial=100, janela=1000, passo=1000, n_vizinhos=20):
        self.n_inicial, self.janela, self.passo, self.k = n_inicial, janela, passo, n_vizinhos

    def _novo(self, X):
        k = min(self.k, len(X) - 1)
        return LocalOutlierFactor(n_neighbors=k, novelty=True).fit(X)

    def fit(self, X):
        self.ref = X[: self.n_inicial]
        self.modelo = self._novo(self.ref)
        return self

    def predict(self, X):
        pred = np.empty(len(X), dtype=int)
        for ini in range(0, len(X), self.passo):
            bloco = X[ini : ini + self.passo]
            pred[ini : ini + len(bloco)] = (self.modelo.predict(bloco) == -1).astype(int)
            self.ref = np.vstack([self.ref, bloco])[-self.janela :]
            self.modelo = self._novo(self.ref)
        return pred


def criar_detector(nome: str, seed: int = 42):
    if nome == "if":
        return _Sklearn(IsolationForest(random_state=seed))
    if nome == "lofn":
        return _Sklearn(LocalOutlierFactor(novelty=True))
    if nome == "ocsvm":
        return _Sklearn(OneClassSVM())
    if nome == "lofs":
        return LOFStream()
    raise ValueError(f"Algoritmo desconhecido: {nome}. Use: {', '.join(NOMES)}")
