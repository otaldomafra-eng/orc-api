# ORÇ_API

API privada para consulta de dados SINAPI Tocantins com historico mensal e sincronizacao automatica a partir dos downloads oficiais da CAIXA.

## Status

Projeto em fase inicial. O repositorio comeca privado, mas deve ser mantido com postura de futuro open source:

- sem segredos versionados;
- configuracao via variaveis de ambiente;
- `.env.example` sempre sanitizado;
- dependencias livres/gratuitas quando possivel;
- documentacao suficiente para instalacao local e deploy em VPS.

## Escopo inicial

- SINAPI TO.
- Historico mensal.
- API FastAPI protegida por Bearer Token.
- PostgreSQL local na VPS.
- Sincronizacao automatica com downloads da CAIXA.
- Fallback manual para importacao de ZIP/XLSX oficial.

## Fora do escopo inicial

- SICRO.
- Todas as UFs.
- Frontend.
- Docker.
- OCR/PDF como fonte primaria.

