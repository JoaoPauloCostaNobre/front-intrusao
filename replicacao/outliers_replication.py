"""Replicação experimental de Vieira (2024) — Etapa 1 do TCC Front-Intrusão.

Usa a camada Model da aplicação (backend/model), de modo que o mesmo código
serve para os experimentos e para a aplicação MVC.

Exemplos (na pasta do projeto, com o ambiente virtual ativo):
    python replicacao/outliers_replication.py --dia terca --algos if
    python replicacao/outliers_replication.py --dia sexta --algos if,lofn,lofs
    python replicacao/outliers_replication.py --dia terca --algos ocsvm --max-treino 50000

Os resultados são salvos em resultados/<dia>_<algoritmo>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from model.detectors import NOMES, criar_detector  # noqa: E402
from model.metrics import REFERENCIA_VIEIRA, avaliar  # noqa: E402
from model.preprocessing import ESPERADO, carregar_dia, preprocessar, separar_treino_teste  # noqa: E402


def br(n: int) -> str:
    """Formata 445645 como 445.645."""
    return f"{n:,}".replace(",", ".")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dia", choices=["terca", "sexta"], required=True)
    ap.add_argument("--algos", default="if,lofn,ocsvm,lofs", help="lista separada por vírgula: if,lofn,ocsvm,lofs")
    ap.add_argument("--dados", default=str(RAIZ / "dados"))
    ap.add_argument("--saida", default=str(RAIZ / "resultados"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-treino", type=int, default=None,
                    help="usa no máximo N instâncias de treino (útil para o One-Class SVM, que é muito lento). "
                         "Se usar, registre no TCC que é uma diferença em relação a Vieira (2024).")
    a = ap.parse_args()

    df = preprocessar(carregar_dia(a.dados, a.dia))
    esp = ESPERADO[a.dia]
    print(f"Esperado por Vieira (2024): {br(esp['instancias'])} instâncias, {br(esp['ataques'])} ataques")

    X_tr, X_te, y_te = separar_treino_teste(df, seed=a.seed)
    print(f"Treino: {br(len(X_tr))} | Teste: {br(len(X_te))} ({br(int(y_te.sum()))} ataques)")

    Path(a.saida).mkdir(parents=True, exist_ok=True)
    for alg in a.algos.split(","):
        alg = alg.strip()
        Xt = X_tr
        if a.max_treino and len(Xt) > a.max_treino and alg != "lofs":
            idx = np.random.default_rng(a.seed).choice(len(Xt), a.max_treino, replace=False)
            Xt = Xt[idx]
            print(f"[{NOMES[alg]}] AVISO: treino reduzido para {br(a.max_treino)} instâncias")
        print(f"\n== {NOMES[alg]} ({a.dia}) — treinando...", flush=True)
        t0 = time.time()
        det = criar_detector(alg, seed=a.seed).fit(Xt)
        pred = det.predict(X_te)
        seg = time.time() - t0
        m = avaliar(y_te, pred)
        ref = REFERENCIA_VIEIRA[a.dia][alg]
        at, no = m["ataque"], m["normal"]
        print(f"Tempo: {seg:.1f} s | Matriz: {m['matriz']}")
        print(f"Ataque  P={at['precisao']:.2f} R={at['revocacao']:.2f} F1={at['f1']:.2f}   (Vieira F1={ref['f1_ataque']:.2f})")
        rp, rr, rf = ref["normal"]
        print(f"Normal  P={no['precisao']:.2f} R={no['revocacao']:.2f} F1={no['f1']:.2f}   (Vieira P={rp:.2f} R={rr:.2f} F1={rf:.2f})")
        out = {"dia": a.dia, "algoritmo": NOMES[alg], "seed": a.seed, "max_treino": a.max_treino,
               "n_treino": int(len(Xt)), "n_teste": int(len(X_te)), "tempo_s": round(seg, 1),
               "metricas": m, "referencia_vieira": ref}
        (Path(a.saida) / f"{a.dia}_{alg}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
