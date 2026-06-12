# Amostra XLSX CAIXA SINAPI

Esta nota registra a estrutura observada em uma amostra oficial de arquivos XLSX extraidos de um ZIP SINAPI da CAIXA, competencia 2026-04.

## Arquivos no ZIP

- `SINAPI_Referencia_2026_04.xlsx`
- `SINAPI_familias_e_coeficientes_2026_04.xlsx`
- `SINAPI_Manutencoes_2026_04.xlsx`
- `SINAPI_mao_de_obra_2026_04.xlsx`

Os nomes publicados pela CAIXA podem conter acentos. O importador deve normalizar nomes de arquivos para matching, mas preservar metadados originais em `raw_data`.

## Workbook de referencia

`SINAPI_Referencia_2026_04.xlsx` contem as abas:

- `Menu`
- `Busca`
- `ISD`
- `ICD`
- `ISE`
- `CSD`
- `CCD`
- `CSE`
- `Analitico`
- `Analitico com Custo`

Abas de insumos:

- `ISD`: insumos com encargos sociais sem desoneracao.
- `ICD`: insumos com encargos sociais com desoneracao.
- `ISE`: insumos sem encargos sociais.

Nas abas de insumos, a linha de cabecalho observada foi a linha 10:

- `Classificacao`
- `Codigo do Insumo`
- `Descricao do Insumo`
- `Unidade`
- `Origem de Preco`
- uma coluna por UF

Na amostra, a coluna `TO` apareceu na coluna 32. O parser deve localizar a coluna pelo texto `TO`, nao por posicao fixa.

Abas de composicoes:

- `CSD`: composicoes com encargos sociais sem desoneracao.
- `CCD`: composicoes com encargos sociais com desoneracao.
- `CSE`: composicoes sem encargos sociais.

Nas abas de composicoes, a linha de cabecalho observada foi a linha 10:

- `Grupo`
- `Codigo da Composicao`
- `Descricao`
- `Unidade`
- pares repetidos de `Custo (R$)` e `%AS` por UF

Na amostra, a UF `TO` apareceu como marcador na linha 9, coluna 57. O valor de custo de TO fica na coluna 57 e o `%AS` correspondente na coluna 58. O parser deve localizar a UF na linha de UFs e associar o par de colunas ao cabecalho da linha 10.

A aba `Analitico` tem itens de composicao:

- linha de cabecalho observada: linha 10
- colunas: `Grupo`, `Codigo da Composicao`, `Tipo Item`, `Codigo do Item`, `Descricao`, `Unidade`, `Coeficiente`, `Situacao`

## Familias e coeficientes

`SINAPI_familias_e_coeficientes_2026_04.xlsx` contem a aba `Coeficientes`.

Linha de cabecalho observada: linha 6.

Colunas iniciais:

- `Codigo da Familia`
- `Codigo do Insumo`
- `Descricao do Insumo`
- `Unidade`
- `Categoria`
- uma coluna por UF

Na amostra, `TO` apareceu na coluna 32.

## Manutencoes

`SINAPI_Manutencoes_2026_04.xlsx` contem a aba `Manutencoes`.

Linha de cabecalho observada: linha 6.

Colunas:

- `Referencia`
- `Tipo`
- `Codigo`
- `Descricao`
- `Manutencao`

Este arquivo nao e especifico por UF na amostra. Ele deve ser importado como historico de manutencoes da competencia.

## Mao de obra

`SINAPI_mao_de_obra_2026_04.xlsx` contem as abas:

- `SEM Desoneracao`
- `COM Desoneracao`

Linha de cabecalho observada: linha 6.

Colunas iniciais:

- `Grupo`
- `Codigo da Composicao`
- `Descricao`
- `Unidade`
- uma coluna por UF

Na amostra, `TO` apareceu na coluna 31.

## Implicacoes para o parser

- Sempre extrair ZIP em diretorio temporario controlado.
- Aceitar XLSX direto no fallback manual.
- Normalizar nomes de abas/cabecalhos para comparacao sem acentos, quebras de linha ou diferenca de caixa.
- Ler `Mes de Referencia` e `Data de emissao` do workbook, mas validar tambem contra ano/mes extraidos do nome do arquivo.
- Localizar `TO` dinamicamente por aba.
- Transformar planilhas largas por UF em registros normalizados.
- Tratar celulas vazias ou hifen como ausencia de preco/custo.
- Persistir valores brutos relevantes em `raw_data` para auditoria e reprocessamento futuro.
