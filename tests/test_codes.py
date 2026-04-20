"""Tests for bcbpy.codes — series code registry."""

from bcbpy.codes import (
    EXCHANGE_RATES,
    INTEREST_RATES,
    INFLATION,
    IPCA_BREAKDOWN,
    IPCA_CATEGORIES,
    GDP,
    EMPLOYMENT,
    INDUSTRIAL_PRODUCTION,
    FINANCIAL_MARKETS,
    SAVINGS,
    CONFIDENCE,
    ECONOMIC_ACTIVITY,
    BASIC_BASKET,
    EXCHANGE_RATE_INDEX,
    CATEGORIES,
    ALL_CODES,
)


class TestCodeDictionaries:
    def test_all_categories_are_registered(self):
        assert len(CATEGORIES) == 14

    def test_all_codes_merged_count(self):
        total = sum(len(d) for d in CATEGORIES.values())
        assert len(ALL_CODES) == total

    def test_no_duplicate_codes_across_categories(self):
        all_values = []
        for d in CATEGORIES.values():
            all_values.extend(d.values())
        assert len(all_values) == len(set(all_values)), "Duplicate SGS codes found across categories"

    def test_all_codes_are_positive_integers(self):
        for name, code in ALL_CODES.items():
            assert isinstance(code, int), f"{name} code is not int: {type(code)}"
            assert code > 0, f"{name} code is not positive: {code}"

    def test_well_known_codes(self):
        assert EXCHANGE_RATES["USD_SALE_DAILY"] == 1
        assert INTEREST_RATES["CDI_DAILY"] == 12
        assert INTEREST_RATES["SELIC_DAILY"] == 11
        assert INFLATION["IPCA"] == 433
        assert INFLATION["IGP_M"] == 189
        assert GDP["GDP_CURRENT_PRICES"] == 1207
        assert EMPLOYMENT["UNEMPLOYMENT_RATE"] == 24369
        assert ECONOMIC_ACTIVITY["IBC_BR_SA"] == 24364

    def test_category_sizes(self):
        assert len(EXCHANGE_RATES) == 6
        assert len(INTEREST_RATES) == 10
        assert len(INFLATION) == 17
        assert len(IPCA_BREAKDOWN) == 11
        assert len(IPCA_CATEGORIES) == 9
        assert len(GDP) == 13
        assert len(EMPLOYMENT) == 7
        assert len(INDUSTRIAL_PRODUCTION) == 7
        assert len(FINANCIAL_MARKETS) == 7
        assert len(SAVINGS) == 2
        assert len(CONFIDENCE) == 4
        assert len(ECONOMIC_ACTIVITY) == 1
        assert len(BASIC_BASKET) == 16
        assert len(EXCHANGE_RATE_INDEX) == 5

    def test_categories_dict_values_match_module_dicts(self):
        assert CATEGORIES["EXCHANGE_RATES"] is EXCHANGE_RATES
        assert CATEGORIES["INTEREST_RATES"] is INTEREST_RATES
        assert CATEGORIES["INFLATION"] is INFLATION
        assert CATEGORIES["GDP"] is GDP

    def test_all_keys_are_uppercase_snake_case(self):
        import re
        pattern = re.compile(r"^[A-Z0-9_]+$")
        for name in ALL_CODES:
            assert pattern.match(name), f"Key '{name}' is not UPPER_SNAKE_CASE"
