"""BCB SGS API constants and configuration."""

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
LAST_N_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/{n}"
DATE_FORMAT = "%d/%m/%Y"
DEFAULT_FORMAT = "json"
MAX_DATE_RANGE_YEARS = 10
