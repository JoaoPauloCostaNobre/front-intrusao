# Controller (Etapa 2)

API REST em FastAPI. Rotas previstas (Figura 4 do TCC):
- `POST /upload` — recebe e valida o CSV de tráfego.
- `POST /deteccao` — executa os algoritmos escolhidos (chama backend/model).
- `POST /explicacao` — pede ao serviço de LLM a explicação dos resultados.

Ainda não implementado — será construído depois que a replicação estiver validada.
