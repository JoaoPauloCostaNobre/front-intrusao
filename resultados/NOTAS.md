# Notas da replicação (diferenças em relação a Vieira, 2024)

Registre aqui cada execução e cada diferença de metodologia. Isto alimenta o Capítulo 3 (Método).

| Data | Dia | Algoritmo | Treino usado | F1 Ataque obtido | F1 Vieira | Observação |
|------|-----|-----------|--------------|------------------|-----------|------------|

## Diferenças conhecidas
- LOF-Stream: implementação própria com janela deslizante (backend/model/detectors.py), equivalente
  à abordagem PySAD/PyOD de Vieira; ela não informa tamanho da janela nem limiar. Janela e passo = 1000.
