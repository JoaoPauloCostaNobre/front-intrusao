# Front-Intrusão

TCC — aplicação MVC para detecção de intrusão com detecção de outliers e explicações por LLM.

## Primeiros passos (Windows / PowerShell, na pasta do projeto)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Depois coloque os CSVs do CICIDS2017 em `dados\` (ver `dados\LEIA-ME.md`) e rode:
```powershell
python replicacao\outliers_replication.py --dia terca --algos if
```
Comece pelo Isolation Forest (mais rápido). O One-Class SVM pode levar horas com a base inteira;
para testar use `--max-treino 50000` e registre isso em `resultados\NOTAS.md`.
