# Front-Intrusão

Aplicação web para **detecção de intrusão em redes** com algoritmos de **detecção de outliers**,
apresentação de métricas de desempenho e **explicação dos resultados em linguagem natural por um
modelo de linguagem (LLM)**.

Trabalho de Conclusão de Curso — Bacharelado em Ciência da Computação
**Instituto Federal Goiano – Campus Morrinhos**

| | |
|---|---|
| **Autor** | João Paulo Costa Nobre |
| **Orientador** | Prof. Dr. Rodrigo Elias |
| **Conclusão prevista** | meados de 2027 |

---

## Sumário
1. [Objetivo](#objetivo)
2. [Arquitetura (MVC)](#arquitetura-mvc)
3. [Estrutura de pastas](#estrutura-de-pastas)
4. [Metodologia replicada (Vieira, 2024)](#metodologia-replicada-vieira-2024)
5. [Resultados de referência](#resultados-de-referência)
6. [Instalação](#instalação)
7. [Obtenção dos dados](#obtenção-dos-dados)
8. [Executando a replicação](#executando-a-replicação)
9. [Situação do projeto](#situação-do-projeto)
10. [Referências](#referências)

---

## Objetivo

Sistemas de detecção de intrusão baseados em anomalias aprendem o comportamento **normal** do
tráfego e sinalizam como suspeito o que foge desse padrão. Os resultados desses algoritmos (matriz de
confusão, precisão, revocação, F1) são difíceis de interpretar para quem não é especialista.

O Front-Intrusão propõe uma aplicação que:

1. recebe dados de tráfego de rede (base **CICIDS2017**);
2. executa algoritmos de detecção de outliers sobre eles;
3. exibe as métricas de avaliação de cada algoritmo e a comparação entre eles;
4. usa um **LLM** para explicar os resultados em linguagem natural.

A primeira etapa do trabalho é a **replicação do estudo correlato de Vieira (2024, UFU)**, para
validar que os algoritmos e o pré-processamento estão corretos antes de construir a aplicação.

---

## Arquitetura (MVC)

A aplicação segue o padrão **Model–View–Controller**:

```
┌──────────────┐   HTTP/JSON   ┌──────────────────┐   chamadas Python   ┌────────────────────────┐
│     View     │ ────────────▶ │    Controller    │ ──────────────────▶ │         Model          │
│ React + Vite │ ◀──────────── │ API REST FastAPI │ ◀────────────────── │ pré-processamento,     │
│  (frontend/) │               │ (backend/        │                     │ algoritmos, métricas,  │
└──────────────┘               │  controller/)    │                     │ serviço LLM            │
                               └──────────────────┘                     │ (backend/model/)       │
                                                                        └────────────────────────┘
```

| Camada | Pasta | Tecnologia | Responsabilidade |
|---|---|---|---|
| **Model** | `backend/model/` | Python, pandas, scikit-learn | Pré-processamento, algoritmos de detecção, métricas, serviço de LLM e persistência |
| **Controller** | `backend/controller/` | FastAPI | Recebe as requisições da interface e aciona o Model |
| **View** | `frontend/` | React + Vite | Apenas interface; nenhum processamento de dados |

Os scripts de experimento em `replicacao/` **reutilizam a mesma camada Model** da aplicação. Assim,
o código validado na replicação é exatamente o código usado pela aplicação final.

### Rotas previstas da API

| Método | Rota | Função |
|---|---|---|
| `POST` | `/upload` | Recebe e valida o CSV de tráfego |
| `POST` | `/deteccao` | Executa os algoritmos escolhidos |
| `POST` | `/explicacao` | Solicita ao LLM a explicação dos resultados |

---

## Estrutura de pastas

```
front-intrusao/
├── backend/
│   ├── model/
│   │   ├── preprocessing.py   # carga e limpeza do CICIDS2017, divisão treino/teste
│   │   ├── detectors.py       # Isolation Forest, LOF, One-Class SVM, LOF-Stream
│   │   └── metrics.py         # matriz de confusão, precisão, revocação, F1
│   └── controller/            # API REST (Etapa 2)
├── frontend/                  # interface React + Vite (Etapa 2)
├── replicacao/
│   └── outliers_replication.py  # script de replicação de Vieira (2024)
├── dados/                     # CSVs do CICIDS2017 (não versionados)
├── resultados/
│   ├── NOTAS.md               # registro de execuções e diferenças de metodologia
│   └── *.json                 # métricas geradas pelos experimentos
└── requirements.txt
```

---

## Metodologia replicada (Vieira, 2024)

### Base de dados
**CICIDS2017** (Canadian Institute for Cybersecurity), versão *MachineLearningCSV*:

| Cenário | Arquivos | Instâncias esperadas | Ataques |
|---|---|---|---|
| **Terça-feira** | `Tuesday-WorkingHours` | 445.645 | 13.832 |
| **Sexta-feira** | `Friday-WorkingHours-Morning`, `-Afternoon-PortScan`, `-Afternoon-DDos` (concatenados) | 702.718 | 288.785 |

### Pré-processamento
1. Remoção das colunas `Fwd Header Length` (duplicada), `Destination Port` e `CWE Flag Count`.
2. Substituição de `Total Fwd Packets` e `Total Backward Packets` pela soma `Total Packets`.
3. Substituição de `Total Length of Fwd Packets` e `Total Length of Bwd Packets` pela soma
   `Total Length of Packets`.
4. Remoção de registros com valores nulos ou infinitos.
5. Rótulo binário: `BENIGN` = 0 (Normal); qualquer ataque = 1 (Ataque).

Resultado esperado: de 79 para 74 colunas (73 atributos + rótulo).

### Divisão treino/teste
- **Treino:** 70% das instâncias **Normais** (os algoritmos aprendem apenas o comportamento normal).
- **Teste:** os 30% restantes das Normais **+ 100% dos Ataques**.

### Algoritmos
Todos com os **parâmetros padrão** da biblioteca, como em Vieira (2024):

| Sigla | Algoritmo | Observação |
|---|---|---|
| `if` | Isolation Forest | scikit-learn |
| `lofn` | Local Outlier Factor (modo *novelty*) | `novelty=True` |
| `ocsvm` | One-Class SVM | custo alto com a base inteira |
| `lofs` | LOF-Stream | LOF em fluxo, modelo inicial de 100 instâncias |

### Métricas
Precisão, revocação e F1, calculadas com a classe **Ataque** como positiva e também com a classe
**Normal** como positiva, além da matriz de confusão.

---

## Resultados de referência

F1 da classe Ataque publicado por Vieira (2024), usado como alvo da replicação:

| Cenário | Isolation Forest | LOF (novelty) | One-Class SVM | LOF-Stream |
|---|---|---|---|---|
| Terça-feira | 0,26 | 0,22 | 0,43 | 0,17 |
| Sexta-feira | 0,50 | 0,55 | 0,32 | 0,45 |

Os resultados obtidos neste trabalho e todas as diferenças de metodologia em relação a Vieira
(por exemplo, amostragem do treino do One-Class SVM) são registrados em
[`resultados/NOTAS.md`](resultados/NOTAS.md).

---

## Instalação

**Requisitos:** Python 3.10 ou superior (testado com 3.14) e Git. Comandos para Windows/PowerShell:

```powershell
git clone https://github.com/JoaoPauloCostaNobre/front-intrusao.git
cd front-intrusao
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Se o PowerShell bloquear a ativação do ambiente virtual, execute uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Dependências principais
| Pacote | Uso |
|---|---|
| numpy, pandas | manipulação dos dados |
| scikit-learn | algoritmos de detecção e métricas |
| fastapi, uvicorn, python-multipart | API REST (Etapa 2) |

### Chave da API do LLM
A chave **nunca** fica no código. Ela deve ser colocada em um arquivo `.env` na raiz do projeto
(ignorado pelo Git).

---

## Obtenção dos dados

1. Acesse https://www.unb.ca/cic/datasets/ids-2017.html e preencha o formulário de download.
2. Baixe **MachineLearningCSV.zip** e extraia.
3. Copie para a pasta `dados/` apenas:
   - `Tuesday-WorkingHours.pcap_ISCX.csv`
   - `Friday-WorkingHours-Morning.pcap_ISCX.csv`
   - `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`
   - `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`

Os CSVs não são versionados por causa do tamanho.

---

## Executando a replicação

Com o ambiente virtual ativo, na raiz do projeto:

```powershell
# Isolation Forest na terça (mais rápido; bom primeiro teste)
python replicacao\outliers_replication.py --dia terca --algos if

# Vários algoritmos na sexta
python replicacao\outliers_replication.py --dia sexta --algos if,lofn,lofs

# One-Class SVM com treino reduzido (registrar em resultados\NOTAS.md)
python replicacao\outliers_replication.py --dia terca --algos ocsvm --max-treino 50000
```

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `--dia` | (obrigatório) | `terca` ou `sexta` |
| `--algos` | `if,lofn,ocsvm,lofs` | algoritmos separados por vírgula |
| `--dados` | `dados/` | pasta com os CSVs |
| `--saida` | `resultados/` | pasta onde os JSONs são gravados |
| `--seed` | `42` | semente aleatória (reprodutibilidade) |
| `--max-treino` | sem limite | usa no máximo N instâncias de treino (não se aplica ao LOF-Stream) |

### Saída
- No terminal: tempo de execução, matriz de confusão e precisão, revocação e F1 de cada classe,
  lado a lado com os valores de Vieira (2024).
- Em arquivo: `resultados/<dia>_<algoritmo>.json` (ex.: `resultados/terca_if.json`).

> O One-Class SVM pode levar horas com a base completa. Usar `--max-treino` é uma diferença de
> metodologia e deve ser registrada em `resultados/NOTAS.md`.

---

## Situação do projeto

| Etapa | Descrição | Situação |
|---|---|---|
| 1 | Replicação de Vieira (2024): pré-processamento, algoritmos e métricas | em andamento |
| 2 | API REST (Controller) | planejada |
| 2 | Interface React (View) | planejada |
| 3 | Serviço de explicação por LLM | planejada |

---

## Referências

- SHARAFALDIN, I.; LASHKARI, A. H.; GHORBANI, A. A. *Toward Generating a New Intrusion Detection
  Dataset and Intrusion Traffic Characterization*. ICISSP, 2018. (Base CICIDS2017)
- VIEIRA (2024). Trabalho correlato — Universidade Federal de Uberlândia (UFU).
- PEDREGOSA, F. et al. *Scikit-learn: Machine Learning in Python*. JMLR, 2011.
