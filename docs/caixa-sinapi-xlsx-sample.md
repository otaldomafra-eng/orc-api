# Amostras CAIXA SINAPI

Esta nota registra a estrutura observada em uma amostra oficial de arquivos XLSX extraidos de um ZIP SINAPI da CAIXA, competencia 2026-04.

## Modelos historicos de arquivo

Ha pelo menos dois modelos de publicacao que o importador deve tratar:

- modelo atual consolidado: arquivos XLSX com todas as UFs na mesma planilha, exigindo filtro dinamico por coluna `TO`;
- modelo legado ate 2024: arquivos ja separados por estado, portanto o ZIP/arquivo de Tocantins deve ser descoberto pelo nome/metadados e importado sem esperar colunas de todas as UFs.

O pipeline de importacao deve selecionar um adaptador conforme o layout detectado, nao apenas conforme o ano. Use a competencia como pista, mas confirme pela estrutura real dos arquivos.

Layouts sugeridos para `sinapi_importacoes.source_layout`:

- `consolidated_xlsx_all_ufs`
- `legacy_state_specific_xlsx`
- `legacy_state_specific_pdf`
- `unknown`

Para o historico ate 2024, o discovery deve priorizar arquivos cujo nome indique Tocantins, como `_TO_`, `TO_`, `Tocantins` ou equivalente normalizado. Se o arquivo legado trouxer somente TO, grave `uf = TO` em todos os registros importados e nao tente localizar coluna de UF.

Se o legado estiver disponivel apenas em PDF, esse caso deve ser separado do parser XLSX. A primeira versao pode descobrir e registrar esses PDFs como importacoes pendentes/falhas controladas, mas o objetivo de historico desde o inicio exige um adaptador especifico ou uma rotina de conversao auditavel para esses arquivos.

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

## Implicacoes para o parser atual consolidado

- Sempre extrair ZIP em diretorio temporario controlado.
- Aceitar XLSX direto no fallback manual.
- Normalizar nomes de abas/cabecalhos para comparacao sem acentos, quebras de linha ou diferenca de caixa.
- Ler `Mes de Referencia` e `Data de emissao` do workbook, mas validar tambem contra ano/mes extraidos do nome do arquivo.
- Localizar `TO` dinamicamente por aba.
- Transformar planilhas largas por UF em registros normalizados.
- Tratar celulas vazias ou hifen como ausencia de preco/custo.
- Persistir valores brutos relevantes em `raw_data` para auditoria e reprocessamento futuro.

## Implicacoes para o parser legado por estado

- Detectar Tocantins pelo nome/metadados do arquivo antes de baixar ou importar.
- Nao exigir coluna `TO` quando o arquivo ja for especifico do estado.
- Registrar `source_layout` e `source_filename` para permitir reprocessamento.
- Validar competencia pelo nome do arquivo e, quando possivel, pelo conteudo.
- Manter o mesmo modelo normalizado de saida usado no layout atual: `uf`, `ano`, `mes`, `tipo`, `codigo`, `descricao`, `unidade`, valores e `raw_data`.
