"""Pré-processamento da base CICIDS2017, replicando Vieira (2024, Seção 3.2).

Etapas (na ordem descrita pela autora):
  1. remoção do atributo duplicado Fwd Header Length (2ª ocorrência);
  2. remoção dos atributos Destination Port e CWE Flag Count;
  3. soma de Total Fwd Packets + Total Backward Packets;
  4. soma de Total Length of Fwd Packets + Total Length of Bwd Packets;
  5. remoção de instâncias com valores nulos;
  6. remoção de instâncias com valores infinitos;
  7. conversão do rótulo para numérico (BENIGN = 0 / Normal, demais = 1 / Ataque).

Resultado esperado: 79 colunas originais -> 74 (73 atributos + rótulo).
Instâncias esperadas após o pré-processamento (Vieira, 2024):
  terça  = 445.645 (13.832 ataques)
  sexta  = 702.718 (288.785 ataques)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Arquivos do pacote "MachineLearningCSV" do CICIDS2017 usados por Vieira (2024)
ARQUIVOS_POR_DIA = {
    "terca": ["Tuesday-WorkingHours.pcap_ISCX.csv"],
    "sexta": [
        "Friday-WorkingHours-Morning.pcap_ISCX.csv",
        "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
        "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    ],
}

ESPERADO = {
    "terca": {"instancias": 445_645, "ataques": 13_832},
    "sexta": {"instancias": 702_718, "ataques": 288_785},
}

ROTULO = "Label"


def carregar_dia(pasta_dados: str | Path, dia: str) -> pd.DataFrame:
    """Lê e concatena os CSVs de um dia ("terca" ou "sexta")."""
    pasta = Path(pasta_dados)
    partes = []
    for nome in ARQUIVOS_POR_DIA[dia]:
        caminho = pasta / nome
        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho}\n"
                "Baixe o MachineLearningCSV.zip do CICIDS2017 e extraia os CSVs na pasta 'dados'."
            )
        partes.append(pd.read_csv(caminho, encoding="latin-1", low_memory=False))
    return pd.concat(partes, ignore_index=True)


def preprocessar(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Aplica as etapas 1 a 7 e devolve um DataFrame só com números."""
    df = df.copy()
    n_ini, c_ini = df.shape
    # nomes do CSV original têm espaços no início (" Destination Port")
    df.columns = [c.strip() for c in df.columns]

    # 1. duplicado: o pandas renomeia a 2ª ocorrência para "Fwd Header Length.1"
    df = df.drop(columns=["Fwd Header Length.1"], errors="ignore")
    # 2.
    df = df.drop(columns=["Destination Port", "CWE Flag Count"], errors="ignore")
    # 3.
    df["Total Packets"] = df.pop("Total Fwd Packets") + df.pop("Total Backward Packets")
    # 4.
    df["Total Length of Packets"] = (
        df.pop("Total Length of Fwd Packets") + df.pop("Total Length of Bwd Packets")
    )
    # 7. (feito antes da limpeza para o rótulo não ser afetado pela conversão numérica)
    y = (df.pop(ROTULO).astype(str).str.strip().str.upper() != "BENIGN").astype(int)
    X = df.apply(pd.to_numeric, errors="coerce")
    X[ROTULO] = y
    # 5 e 6.
    X = X.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)

    if verbose:
        print(
            f"Pré-processamento: {n_ini:,} -> {len(X):,} instâncias "
            f"({n_ini - len(X):,} removidas); {c_ini} -> {X.shape[1]} colunas; "
            f"ataques = {int(X[ROTULO].sum()):,}".replace(",", ".")
        )
    return X


def separar_treino_teste(df: pd.DataFrame, seed: int = 42, frac_treino: float = 0.7):
    """Divisão de Vieira (2024, Seção 3.4):
    treino = 70% (aleatório) das instâncias Normais;
    teste  = 30% restantes das Normais + 100% dos Ataques.
    Retorna X_treino, X_teste, y_teste (y: 1 = Ataque)."""
    normais = df[df[ROTULO] == 0]
    ataques = df[df[ROTULO] == 1]
    treino = normais.sample(frac=frac_treino, random_state=seed)
    teste = pd.concat([normais.drop(treino.index), ataques]).sample(frac=1.0, random_state=seed)
    X_treino = treino.drop(columns=[ROTULO]).to_numpy(dtype=np.float64)
    X_teste = teste.drop(columns=[ROTULO]).to_numpy(dtype=np.float64)
    y_teste = teste[ROTULO].to_numpy()
    return X_treino, X_teste, y_teste
