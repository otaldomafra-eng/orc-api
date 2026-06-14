# ORÇ_API

API privada para consulta de dados SINAPI Tocantins com historico mensal e sincronizacao automatica a partir dos downloads oficiais da CAIXA.

## Status

Projeto em desenvolvimento. A API ja sobe localmente, cria chaves, importa manualmente XLSX/ZIP SINAPI no layout consolidado atual e permite consultar competencias/itens por HTTP.

O repositorio comeca privado, mas deve ser mantido com postura de futuro open source:

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
- Parser inicial para XLSX consolidado 2025+.
- Registro de layout de origem para suportar legado ate 2024 por estado.

## Fora do escopo inicial

- SICRO.
- Todas as UFs.
- Frontend.
- Docker.
- OCR/PDF como fonte primaria.

## Desenvolvimento local

```powershell
cd "C:\BACKUP_HD_D_2026-05-28\00 - AGENCIA ORKEST\ORÇ_API"
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Para usar SQLite local rapidamente, ajuste no `.env`:

```env
DATABASE_URL=sqlite:///./sinapi-dev.db
API_KEY_PEPPER=troque-por-um-valor-longo-local
```

Inicialize o banco:

```powershell
.\.venv\Scripts\python scripts\init_db.py
```

Crie tokens:

```powershell
.\.venv\Scripts\python scripts\create_api_key.py --name local-read --role read
.\.venv\Scripts\python scripts\create_api_key.py --name local-admin --role admin
```

O script imprime o token uma unica vez. Guarde fora do Git.

Suba a API:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8088/health
```

## Importacao manual

Via CLI:

```powershell
.\.venv\Scripts\python scripts\import_file.py "C:\caminho\para\SINAPI_Referencia_2026_04.xlsx"
```

Via HTTP:

```powershell
$adminToken = "cole-o-token-admin"
Invoke-RestMethod `
  -Uri http://127.0.0.1:8088/api/v1/admin/importacoes/manual `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -Method Post `
  -Form @{ file = Get-Item "C:\caminho\para\SINAPI_Referencia_2026_04.xlsx" }
```

## Consultas

```powershell
$readToken = "cole-o-token-read"
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8088/api/v1/competencias" `
  -Headers @{ Authorization = "Bearer $readToken" }

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8088/api/v1/itens?q=cimento" `
  -Headers @{ Authorization = "Bearer $readToken" }
```

## Testes

```powershell
.\.venv\Scripts\python -m pytest
```

## Estado do parser

- Suportado agora: XLSX consolidado com abas `ISE`, `ISD`, `ICD`, `CSE`, `CSD`, `CCD`, filtrando a coluna `TO`.
- Planejado: arquivos legados ate 2024 separados por estado, em XLSX/PDF, com adaptador separado.
- Planejado: sync automatico completo CAIXA discovery -> download -> importacao.
