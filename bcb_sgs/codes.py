"""
BCB SGS Series Codes — Curated Reference

All codes sourced from https://dadosabertos.bcb.gov.br/
and the SGS series finder at https://www3.bcb.gov.br/sgspub/
"""

# =============================================================================
# Exchange Rates (Taxas de Cambio)
# =============================================================================
EXCHANGE_RATES = {
    "USD_SALE_DAILY": 1,
    "USD_PURCHASE_DAILY": 10813,
    "USD_MONTHLY_PURCHASE_END": 3695,
    "USD_MONTHLY_SALE_END": 3696,
    "USD_MONTHLY_PURCHASE_AVG": 3697,
    "USD_MONTHLY_SALE_AVG": 3698,
}

# =============================================================================
# Interest Rates (Taxas de Juros)
# =============================================================================
INTEREST_RATES = {
    "SELIC_DAILY": 11,
    "CDI_DAILY": 12,
    "TR": 226,
    "TBF": 253,
    "TJLP": 256,
    "SELIC_TARGET": 432,
    "SELIC_OVERNIGHT_ANNUAL": 4189,
    "SELIC_MONTHLY_ACCUMULATED": 4390,
    "CDI_MONTHLY": 4391,
    "CDI_OVERNIGHT": 4392,
}

# =============================================================================
# Inflation Indices (Indices de Precos)
# =============================================================================
INFLATION = {
    "IPCA": 433,
    "INPC": 188,
    "IPCA_15": 7478,
    "IPCA_E": 10764,
    "IPCA_12M_ACCUMULATED": 13522,
    "IGP_M": 189,
    "IGP_DI": 190,
    "IGP_10": 7447,
    "IGP_M_1ST_DECENNIAL": 7448,
    "IGP_M_2ND_DECENNIAL": 7449,
    "IPC_FIPE_MONTHLY": 193,
    "IPC_FIPE_1ST_QUAD": 7463,
    "IPC_FIPE_2ND_QUAD": 272,
    "IPC_FIPE_3RD_QUAD": 7464,
    "IPC_DI": 191,
    "ICV_DIEESE": 194,
    "IPA_DI_GENERAL": 225,
}

# =============================================================================
# IPCA Breakdown (Decomposicao do IPCA)
# =============================================================================
IPCA_BREAKDOWN = {
    "IPCA_FREE_ITEMS": 11428,
    "IPCA_TRADEABLE": 4447,
    "IPCA_NON_TRADEABLE": 4448,
    "IPCA_ADMINISTERED": 4449,
    "IPCA_DURABLE_GOODS": 10843,
    "IPCA_SEMI_DURABLE_GOODS": 10842,
    "IPCA_NON_DURABLE_GOODS": 10841,
    "IPCA_SERVICES": 10844,
    "IPCA_CORE_EX1": 1621,
    "IPCA_CORE_TRIMMED_MEANS": 4466,
    "IPCA_CORE_DP": 16122,
}

# =============================================================================
# IPCA by Category — Monthly % Variation
# =============================================================================
IPCA_CATEGORIES = {
    "FOOD_AND_BEVERAGES": 1635,
    "HOUSING": 1636,
    "HOUSEHOLD_ARTICLES": 1637,
    "CLOTHING": 1638,
    "TRANSPORTATION": 1639,
    "COMMUNICATION": 1640,
    "HEALTH_AND_PERSONAL_CARE": 1641,
    "PERSONAL_EXPENSES": 1642,
    "EDUCATION": 1643,
}

# =============================================================================
# GDP and National Accounts (PIB e Contas Nacionais)
# =============================================================================
GDP = {
    "GDP_CURRENT_PRICES": 1207,
    "GDP_CONSTANT_BRL": 1208,
    "GDP_USD": 7324,
    "POPULATION": 21774,
    "GDP_PER_CAPITA_CURRENT": 21775,
    "GDP_PER_CAPITA_USD": 21776,
    "GDP_QUARTERLY": 22099,
    "GDP_QUARTERLY_SA": 22109,
    "HOUSEHOLD_CONSUMPTION": 22100,
    "GOVERNMENT_CONSUMPTION": 22101,
    "GFCF": 22102,
    "EXPORTS": 22103,
    "IMPORTS": 22104,
}

# =============================================================================
# Employment and Labor (Emprego e Trabalho)
# =============================================================================
EMPLOYMENT = {
    "UNEMPLOYMENT_RATE": 24369,
    "LABOR_FORCE": 24378,
    "EMPLOYED_PERSONS": 24379,
    "UNEMPLOYED_PERSONS": 24380,
    "AVG_REAL_INCOME": 24381,
    "AVG_NOMINAL_INCOME": 24382,
    "FORMAL_EMPLOYMENT_TOTAL": 25239,
}

# =============================================================================
# Industrial Production (Producao Industrial)
# =============================================================================
INDUSTRIAL_PRODUCTION = {
    "PRODUCTION_GENERAL": 21858,
    "PRODUCTION_TOTAL": 21859,
    "MANUFACTURING": 21862,
    "MINING": 21861,
    "CAPITAL_GOODS": 21863,
    "INTERMEDIATE_GOODS": 21864,
    "CONSUMER_GOODS_GENERAL": 21865,
}

# =============================================================================
# Financial Markets and Indices
# =============================================================================
FINANCIAL_MARKETS = {
    "GOLD_BMF_GRAM": 4,
    "GOLD_LONDON_OZ": 5,
    "BOVESPA_INDEX": 7,
    "BOVESPA_VOLUME": 8,
    "IMA_B": 12466,
    "IMA_B5": 12467,
    "IMA_B5_PLUS": 12468,
}

# =============================================================================
# Savings (Poupanca)
# =============================================================================
SAVINGS = {
    "SAVINGS_RATE": 196,
    "SAVINGS_DEPOSITS_RETURN": 25,
}

# =============================================================================
# Consumer and Business Confidence (Indices de Confianca)
# =============================================================================
CONFIDENCE = {
    "ICC_GENERAL": 4393,
    "ICC_FUTURE_EXPECTATIONS": 4394,
    "ICC_CURRENT_CONDITIONS": 4395,
    "ICEI_GENERAL": 7341,
}

# =============================================================================
# Economic Activity
# =============================================================================
ECONOMIC_ACTIVITY = {
    "IBC_BR_SA": 24364,
}

# =============================================================================
# Basic Basket by Capital City (Cesta Basica)
# =============================================================================
BASIC_BASKET = {
    "ARACAJU": 7479,
    "BELEM": 7480,
    "BELO_HORIZONTE": 7481,
    "BRASILIA": 7482,
    "CURITIBA": 7483,
    "FLORIANOPOLIS": 7484,
    "FORTALEZA": 7485,
    "GOIANIA": 7486,
    "JOAO_PESSOA": 7487,
    "NATAL": 7488,
    "PORTO_ALEGRE": 7489,
    "RECIFE": 7490,
    "RIO_DE_JANEIRO": 7491,
    "SALVADOR": 7492,
    "SAO_PAULO": 7493,
    "VITORIA": 7494,
}

# =============================================================================
# Real Effective Exchange Rate Index (IPCA-based)
# =============================================================================
EXCHANGE_RATE_INDEX = {
    "REER_BASKET": 11752,
    "REER_USD": 11753,
    "REER_JPY": 11754,
    "REER_EUR": 11755,
    "REER_ARS": 11756,
}

# =============================================================================
# Category registry — maps category names to their dicts
# =============================================================================
CATEGORIES = {
    "EXCHANGE_RATES": EXCHANGE_RATES,
    "INTEREST_RATES": INTEREST_RATES,
    "INFLATION": INFLATION,
    "IPCA_BREAKDOWN": IPCA_BREAKDOWN,
    "IPCA_CATEGORIES": IPCA_CATEGORIES,
    "GDP": GDP,
    "EMPLOYMENT": EMPLOYMENT,
    "INDUSTRIAL_PRODUCTION": INDUSTRIAL_PRODUCTION,
    "FINANCIAL_MARKETS": FINANCIAL_MARKETS,
    "SAVINGS": SAVINGS,
    "CONFIDENCE": CONFIDENCE,
    "ECONOMIC_ACTIVITY": ECONOMIC_ACTIVITY,
    "BASIC_BASKET": BASIC_BASKET,
    "EXCHANGE_RATE_INDEX": EXCHANGE_RATE_INDEX,
}

# =============================================================================
# Flat lookup — all codes merged into one dict
# =============================================================================
ALL_CODES = {}
for _category_dict in CATEGORIES.values():
    ALL_CODES.update(_category_dict)
