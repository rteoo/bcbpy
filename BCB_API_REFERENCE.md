# BCB SGS API Reference Guide

Developer reference for the **SGS (Sistema Gerenciador de Series Temporais)** API from the [Banco Central do Brasil](https://dadosabertos.bcb.gov.br/).

Browse/search all available series at:
https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries

---

## Endpoints

**All values for a series:**
```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODE}/dados?formato=json
```

**Last N values:**
```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODE}/dados/ultimos/{N}?formato=json
```

**Date range filter:**
```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODE}/dados?formato=json&dataInicial=01/01/2020&dataFinal=31/12/2024
```

---

## Query Parameters

| Parameter      | Required | Format       | Description              |
|----------------|----------|--------------|--------------------------|
| `formato`      | Yes      | `json`, `csv`| Response format          |
| `dataInicial`  | No       | `DD/MM/YYYY` | Start date (Brazilian)   |
| `dataFinal`    | No       | `DD/MM/YYYY` | End date (Brazilian)     |

---

## Response Format (JSON)

```json
[
  { "data": "13/04/2026", "valor": "1.234" }
]
```

- `data` — date in DD/MM/YYYY format (string)
- `valor` — value as string (convert to float for calculations)

---

## API Limits and Notes

- **Date range limit (since March 2025):** queries are capped at **10 years** max. Using date filters is now mandatory for large series.
- **Rate limiting:** HTTP 429 on excessive requests (no official limit documented).
- **Dates use DD/MM/YYYY** (Brazilian format). The `bcbpy` client also accepts YYYY-MM-DD for convenience.
- **HTTP 404** is returned for invalid series codes.
- **Empty arrays** are returned when a valid series has no data in the requested range.

---

## Series Code Reference

### Exchange Rates (Taxas de Cambio)

| Code  | Key Name                  | Description                         |
|-------|---------------------------|-------------------------------------|
| 1     | `USD_SALE_DAILY`          | USD/BRL - Free rate - sale (daily)  |
| 10813 | `USD_PURCHASE_DAILY`      | USD/BRL - Free rate - purchase (daily) |
| 3695  | `USD_MONTHLY_PURCHASE_END`| USD monthly, purchase, end of period |
| 3696  | `USD_MONTHLY_SALE_END`    | USD monthly, sale, end of period    |
| 3697  | `USD_MONTHLY_PURCHASE_AVG`| USD monthly, purchase, period average |
| 3698  | `USD_MONTHLY_SALE_AVG`    | USD monthly, sale, period average   |

### Interest Rates (Taxas de Juros)

| Code  | Key Name                    | Description                          |
|-------|-----------------------------|--------------------------------------|
| 11    | `SELIC_DAILY`               | Selic rate (daily)                   |
| 12    | `CDI_DAILY`                 | CDI rate (daily)                     |
| 226   | `TR`                        | Taxa Referencial                     |
| 253   | `TBF`                       | Taxa Basica Financeira               |
| 256   | `TJLP`                      | Taxa de Juros de Longo Prazo         |
| 432   | `SELIC_TARGET`              | Selic target rate (meta)             |
| 4189  | `SELIC_OVERNIGHT_ANNUAL`    | Selic overnight annualized (base 252)|
| 4390  | `SELIC_MONTHLY_ACCUMULATED` | Selic accumulated monthly            |
| 4391  | `CDI_MONTHLY`               | CDI monthly                          |
| 4392  | `CDI_OVERNIGHT`             | CDI overnight                        |

### Inflation Indices (Indices de Precos)

| Code  | Key Name              | Description                          |
|-------|-----------------------|--------------------------------------|
| 433   | `IPCA`                | IPCA (official inflation index)      |
| 188   | `INPC`                | INPC                                 |
| 7478  | `IPCA_15`             | IPCA-15                              |
| 10764 | `IPCA_E`              | IPCA-E                               |
| 13522 | `IPCA_12M_ACCUMULATED`| IPCA accumulated 12 months           |
| 189   | `IGP_M`               | IGP-M                                |
| 190   | `IGP_DI`              | IGP-DI                               |
| 7447  | `IGP_10`              | IGP-10                               |
| 7448  | `IGP_M_1ST_DECENNIAL` | IGP-M 1st decennial                  |
| 7449  | `IGP_M_2ND_DECENNIAL` | IGP-M 2nd decennial                  |
| 193   | `IPC_FIPE_MONTHLY`    | IPC-Fipe monthly                     |
| 7463  | `IPC_FIPE_1ST_QUAD`   | IPC-Fipe 1st quadriweek              |
| 272   | `IPC_FIPE_2ND_QUAD`   | IPC-Fipe 2nd quadriweek              |
| 7464  | `IPC_FIPE_3RD_QUAD`   | IPC-Fipe 3rd quadriweek              |
| 191   | `IPC_DI`              | IPC-DI                               |
| 194   | `ICV_DIEESE`          | ICV-Dieese (Cost of Living)          |
| 225   | `IPA_DI_GENERAL`      | IPA-DI general                       |

### IPCA Breakdown (Decomposicao do IPCA)

| Code  | Key Name                  | Description                          |
|-------|---------------------------|--------------------------------------|
| 11428 | `IPCA_FREE_ITEMS`         | IPCA - Free items                    |
| 4447  | `IPCA_TRADEABLE`          | IPCA - Tradeable goods               |
| 4448  | `IPCA_NON_TRADEABLE`      | IPCA - Non-tradeable goods           |
| 4449  | `IPCA_ADMINISTERED`       | IPCA - Administered/monitored prices |
| 10843 | `IPCA_DURABLE_GOODS`      | IPCA - Durable goods                 |
| 10842 | `IPCA_SEMI_DURABLE_GOODS` | IPCA - Semi-durable goods            |
| 10841 | `IPCA_NON_DURABLE_GOODS`  | IPCA - Non-durable goods             |
| 10844 | `IPCA_SERVICES`           | IPCA - Services                      |
| 1621  | `IPCA_CORE_EX1`           | IPCA Core - Ex-1                     |
| 4466  | `IPCA_CORE_TRIMMED_MEANS` | IPCA Core - MS (trimmed means)       |
| 16122 | `IPCA_CORE_DP`            | IPCA Core - DP                       |

### IPCA by Category (monthly % variation)

| Code  | Key Name                  | Category                                      |
|-------|---------------------------|-----------------------------------------------|
| 1635  | `FOOD_AND_BEVERAGES`      | Alimentacao e bebidas                         |
| 1636  | `HOUSING`                 | Habitacao                                     |
| 1637  | `HOUSEHOLD_ARTICLES`      | Artigos de residencia                         |
| 1638  | `CLOTHING`                | Vestuario                                     |
| 1639  | `TRANSPORTATION`          | Transportes                                   |
| 1640  | `COMMUNICATION`           | Comunicacao                                   |
| 1641  | `HEALTH_AND_PERSONAL_CARE`| Saude e cuidados pessoais                     |
| 1642  | `PERSONAL_EXPENSES`       | Despesas pessoais                             |
| 1643  | `EDUCATION`               | Educacao                                      |

### GDP and National Accounts (PIB e Contas Nacionais)

| Code  | Key Name                | Description                          |
|-------|-------------------------|--------------------------------------|
| 1207  | `GDP_CURRENT_PRICES`    | GDP at current prices                |
| 1208  | `GDP_CONSTANT_BRL`      | GDP in constant R$                   |
| 7324  | `GDP_USD`               | GDP in USD                           |
| 21774 | `POPULATION`            | Population                           |
| 21775 | `GDP_PER_CAPITA_CURRENT`| GDP per capita at current prices     |
| 21776 | `GDP_PER_CAPITA_USD`    | GDP per capita in USD                |
| 22099 | `GDP_QUARTERLY`         | Quarterly GDP                        |
| 22109 | `GDP_QUARTERLY_SA`      | Quarterly GDP seasonally adjusted    |
| 22100 | `HOUSEHOLD_CONSUMPTION` | Household consumption                |
| 22101 | `GOVERNMENT_CONSUMPTION`| Government consumption               |
| 22102 | `GFCF`                  | Gross Fixed Capital Formation        |
| 22103 | `EXPORTS`               | Exports                              |
| 22104 | `IMPORTS`               | Imports                              |

### Employment and Labor (Emprego e Trabalho)

| Code  | Key Name                 | Description                          |
|-------|--------------------------|--------------------------------------|
| 24369 | `UNEMPLOYMENT_RATE`      | Unemployment rate                    |
| 24378 | `LABOR_FORCE`            | Labor force                          |
| 24379 | `EMPLOYED_PERSONS`       | Employed persons                     |
| 24380 | `UNEMPLOYED_PERSONS`     | Unemployed persons                   |
| 24381 | `AVG_REAL_INCOME`        | Average real income (deflated)       |
| 24382 | `AVG_NOMINAL_INCOME`     | Average nominal income               |
| 25239 | `FORMAL_EMPLOYMENT_TOTAL`| Formal employment - total            |

### Industrial Production (Producao Industrial)

| Code  | Key Name               | Description                          |
|-------|------------------------|--------------------------------------|
| 21858 | `PRODUCTION_GENERAL`   | Industrial production - general      |
| 21859 | `PRODUCTION_TOTAL`     | Industrial production - total        |
| 21862 | `MANUFACTURING`        | Manufacturing industry               |
| 21861 | `MINING`               | Mining                               |
| 21863 | `CAPITAL_GOODS`        | Capital goods                        |
| 21864 | `INTERMEDIATE_GOODS`   | Intermediate goods                   |
| 21865 | `CONSUMER_GOODS_GENERAL`| Consumer goods - general            |

### Financial Markets and Indices

| Code  | Key Name          | Description                          |
|-------|-------------------|--------------------------------------|
| 4     | `GOLD_BMF_GRAM`   | BM&F Gold (gram)                     |
| 5     | `GOLD_LONDON_OZ`  | Gold London (troy ounce)             |
| 7     | `BOVESPA_INDEX`   | Bovespa index                        |
| 8     | `BOVESPA_VOLUME`  | Bovespa total volume                 |
| 12466 | `IMA_B`           | IMA-B (daily)                        |
| 12467 | `IMA_B5`          | IMA-B5 (daily)                       |
| 12468 | `IMA_B5_PLUS`     | IMA-B5+ (daily)                      |

### Savings (Poupanca)

| Code  | Key Name                | Description                          |
|-------|-------------------------|--------------------------------------|
| 196   | `SAVINGS_RATE`          | Savings rate                         |
| 25    | `SAVINGS_DEPOSITS_RETURN`| Savings deposits return (pre-05/2012)|

### Consumer and Business Confidence (Indices de Confianca)

| Code  | Key Name                   | Description                          |
|-------|----------------------------|--------------------------------------|
| 4393  | `ICC_GENERAL`              | Consumer confidence - general        |
| 4394  | `ICC_FUTURE_EXPECTATIONS`  | Consumer confidence - future         |
| 4395  | `ICC_CURRENT_CONDITIONS`   | Consumer confidence - current        |
| 7341  | `ICEI_GENERAL`             | Business confidence - general        |

### Economic Activity

| Code  | Key Name     | Description                          |
|-------|--------------|--------------------------------------|
| 24364 | `IBC_BR_SA`  | IBC-Br seasonally adjusted           |

### Basic Basket by Capital City (Cesta Basica)

| Code  | Key Name          | City           |
|-------|-------------------|----------------|
| 7479  | `ARACAJU`         | Aracaju        |
| 7480  | `BELEM`           | Belem          |
| 7481  | `BELO_HORIZONTE`  | Belo Horizonte |
| 7482  | `BRASILIA`        | Brasilia       |
| 7483  | `CURITIBA`        | Curitiba       |
| 7484  | `FLORIANOPOLIS`   | Florianopolis  |
| 7485  | `FORTALEZA`       | Fortaleza      |
| 7486  | `GOIANIA`         | Goiania        |
| 7487  | `JOAO_PESSOA`     | Joao Pessoa    |
| 7488  | `NATAL`           | Natal          |
| 7489  | `PORTO_ALEGRE`    | Porto Alegre   |
| 7490  | `RECIFE`          | Recife         |
| 7491  | `RIO_DE_JANEIRO`  | Rio de Janeiro |
| 7492  | `SALVADOR`        | Salvador       |
| 7493  | `SAO_PAULO`       | Sao Paulo      |
| 7494  | `VITORIA`         | Vitoria        |

### Real Effective Exchange Rate Index (IPCA-based)

| Code  | Key Name      | Description                          |
|-------|---------------|--------------------------------------|
| 11752 | `REER_BASKET` | Basket (cesta de moedas)             |
| 11753 | `REER_USD`    | US Dollar                            |
| 11754 | `REER_JPY`    | Japanese Yen                         |
| 11755 | `REER_EUR`    | Euro                                 |
| 11756 | `REER_ARS`    | Argentine Peso                       |

---

## Python Usage Examples

### Using the bcbpy package (this project)

```python
from bcbpy import fetch_series, fetch_last, fetch_multiple
from bcbpy import INTEREST_RATES, EXCHANGE_RATES, INFLATION

# Fetch CDI daily rate for 2024
cdi = fetch_series(INTEREST_RATES["CDI_DAILY"], start_date="2024-01-01", end_date="2024-12-31")

# Last 10 USD/BRL rates
usd = fetch_last(EXCHANGE_RATES["USD_SALE_DAILY"], n=10)

# Multiple series merged into one DataFrame
df = fetch_multiple(
    {"CDI": INTEREST_RATES["CDI_DAILY"], "SELIC": INTEREST_RATES["SELIC_DAILY"]},
    start_date="2024-01-01",
    end_date="2024-12-31",
)

# Search available codes
from bcbpy import search_codes, list_codes
search_codes("IPCA")           # find all IPCA-related codes
list_codes("INTEREST_RATES")   # list all interest rate codes
```

### Using requests + pandas (direct API calls)

```python
import pandas as pd

def consulta_bc(codigo_bcb, data_inicio=None, data_fim=None):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_bcb}/dados?formato=json'
    if data_inicio:
        url += f'&dataInicial={data_inicio}&dataFinal={data_fim}'
    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df.set_index('data', inplace=True)
    return df

# CDI daily (dates in DD/MM/YYYY)
cdi = consulta_bc(12, '01/01/2024', '31/12/2024')

# Last 10 USD rates
url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/10?formato=json'
dolar = pd.read_json(url)
```

---

## Data Source

All data is provided by the [BCB Open Data Portal](https://dadosabertos.bcb.gov.br/) under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/). The portal hosts 4,100+ datasets across all BCB departments.
