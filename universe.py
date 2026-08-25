# -*- coding: utf-8 -*-
"""The Halal Market Ledger universe: 60 Shariah-screened securities."""

US_STOCKS = ["AAPL","NVDA","AVGO","ASML","ORCL","LLY","JNJ","ABT","PG","HD","LIN","XOM",
             "AMD","QCOM","TXN","MU","AMAT","LRCX","MSFT","GOOGL","CRM","ADBE","NOW","PANW",
             "MRK","DHR","ISRG","SYK","VRTX","REGN","NKE","TJX","COP","EOG","NEM"]

CA_STOCKS = ["AEM","CCO","SHOP","DSG","CSU","CNR","CP","CNQ","SU","CVE","WCN","STN","IMO"]

FUNDS = [
    ("SPUS","Equity ETF","US large-cap Shariah (S&P 500 exclusions)"),
    ("HLAL","Equity ETF","US large-cap Shariah (FTSE USA)"),
    ("SPTE","Equity ETF","Global technology Shariah"),
    ("SPWO","Equity ETF","Developed world ex-US Shariah equity"),
    ("UMMA","Equity ETF","Global ex-US Islamic equity"),
    ("SPRE","Equity ETF","Global REITs Shariah"),
    ("SPSK","Sukuk / Fixed Income ETF","Sukuk / Islamic fixed income"),
    ("MNZL","Equity ETF","US broad-market halal"),
    ("WSHR.NE","Equity ETF","Global developed Shariah equity (Canada-listed)"),
    ("AMAGX","Mutual Fund","Islamic global growth equity"),
    ("AMANX","Mutual Fund","Islamic income / dividend equity"),
    ("AMDWX","Mutual Fund","Islamic emerging markets equity"),
]

# Shariah index membership, refreshed from the issuers' published holdings files.
# True = held, False = not held. Update when you re-check sp-funds.com / wahedinvest.com.
SCREENS = {t: {"spus": True, "hlal": True} for t in US_STOCKS}
SCREENS["ORCL"] = {"spus": True,  "hlal": False}   # FTSE screens debt vs total assets
SCREENS["HD"]   = {"spus": True,  "hlal": False}
SCREENS["ASML"] = {"spus": False, "hlal": False}   # NL domicile — US-only universes
SCREENS_ASOF = "2026-08-24"

# Names deliberately excluded from the universe.
EXCLUDED = ["MCD","CMG","DE","HON","GE","LMT","RTX","TMUS","DIS","AMGN"]
QUESTIONABLE = ["COST","WMT","NFLX","SBUX","INTU","CAT"]

# Documented data facts, so the report can distinguish "missing" from "genuinely absent".
NO_DEBT = {"ISRG"}          # D/E absent because there is no meaningful debt
