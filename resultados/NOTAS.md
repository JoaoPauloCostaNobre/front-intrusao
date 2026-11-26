# Notas do projeto Front-Intrusão

Registro contínuo de tudo o que é feito no projeto: ambiente, decisões, execuções e diferenças de
metodologia em relação a Vieira (2024). Serve de fonte para a escrita do TCC, principalmente do
Capítulo 3 (Método) e do Capítulo 4 (Resultados).

**Como ler:** a seção 1 descreve o ambiente; a seção 2 é a tabela de execuções dos experimentos;
a seção 3 lista as diferenças de metodologia; a seção 4 é o diário, em ordem cronológica.

---

## 1. Ambiente de execução

| Item | Versão |
|---|---|
| Sistema operacional | Windows 11 Pro (10.0.26200) |
| Python | 3.14.7 |
| numpy | 2.5.5 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| FastAPI | 0.165.0 |
| Uvicorn | 0.54.0 |
| Git | 2.56.1 |

As bibliotecas foram instaladas em um ambiente virtual (`.venv`) a partir do `requirements.txt`,
que fixa apenas versões mínimas (`>=`). As versões acima são as efetivamente instaladas.

**Observação para o texto:** essas versões são mais recentes que as disponíveis em 2024, quando
Vieira realizou o estudo. Mudanças internas das bibliotecas (por exemplo, o pandas 3 alterou o
tratamento de colunas de texto e de cópias de tabelas) podem causar pequenas diferenças numéricas
nos resultados, mesmo com a mesma metodologia.

---

## 2. Execuções dos experimentos

| Data | Dia | Algoritmo | Treino usado | F1 Ataque obtido | F1 Vieira | Observação |
|------|-----|-----------|--------------|------------------|-----------|------------|

*(Nenhuma execução ainda: aguardando os CSVs do CICIDS2017 na pasta `dados/`.)*

---

## 3. Diferenças de metodologia em relação a Vieira (2024)

- **LOF-Stream:** implementação própria com janela deslizante (`backend/model/detectors.py`,
  classe `LOFStream`), equivalente à abordagem PySAD/PyOD de Vieira. O trabalho de Vieira não
  informa o tamanho da janela nem o limiar. Valores adotados aqui:
  - modelo inicial: 100 primeiras instâncias do treino (igual a Vieira);
  - janela de referência: 1000 instâncias;
  - passo de retreino: a cada 1000 instâncias de teste;
  - vizinhos (k): 20 (padrão do scikit-learn);
  - limiar: o padrão do LOF do scikit-learn.

  Funcionamento: as instâncias de teste chegam em blocos; cada bloco é classificado pelo modelo
  atual, entra na janela, e o LOF é retreinado com as últimas 1000 instâncias.
- **Versões das bibliotecas:** mais recentes que as de Vieira (ver seção 1).
- **Semente aleatória:** 42, usada na divisão treino/teste e nos algoritmos que têm aleatoriedade.
  Vieira não informa a semente usada.

---

## 4. Diário de atividades

### 26/11/2026 — Preparação do ambiente e do repositório
- Verificado o Python 3.14.7 já instalado. Instalado o Git 2.56.1 pelo gerenciador `winget`.
- Criado o ambiente virtual `.venv` e instaladas as dependências do `requirements.txt` (versões
  na seção 1). Testada a importação de numpy, pandas, scikit-learn e FastAPI: sem erros.
- Criado o repositório Git (branch `main`) e publicado no GitHub:
  https://github.com/JoaoPauloCostaNobre/front-intrusao
- Conferido que os dados do CICIDS2017 (`dados/*.csv`) e o arquivo de segredos `.env` não são
  versionados (`.gitignore`).
- Estado do código nesse momento (Etapa 1):
  - `backend/model/preprocessing.py`: carga dos CSVs por dia, pré-processamento em 7 etapas
    (seção 3.2 de Vieira) e divisão treino/teste (70% dos Normais / 30% dos Normais + 100% dos
    Ataques);
  - `backend/model/detectors.py`: Isolation Forest, LOF (novelty), One-Class SVM e LOF-Stream,
    todos com parâmetros padrão; a saída é convertida para 0 = Normal e 1 = Ataque;
  - `backend/model/metrics.py`: matriz de confusão, precisão, revocação e F1 para as duas
    classes;
  - `replicacao/outliers_replication.py`: script que executa o experimento e salva
    `resultados/<dia>_<algoritmo>.json`.
- README reescrito com a documentação completa do projeto: objetivo, arquitetura MVC,
  metodologia, resultados de referência, instalação e execução.
- **Próximo passo:** baixar os CSVs do CICIDS2017 e executar o Isolation Forest no cenário de
  terça-feira, conferindo se o pré-processamento chega a 445.645 instâncias (13.832 ataques).
