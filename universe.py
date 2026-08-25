# -*- coding: utf-8 -*-
"""The Halal Market Ledger universe: 112 Shariah-screened securities."""

US_STOCKS = ["AAPL","NVDA","AVGO","ASML","ORCL","LLY","JNJ","ABT","PG","HD","LIN","XOM",
             "AMD","QCOM","TXN","MU","AMAT","LRCX","MSFT","GOOGL","CRM","ADBE","NOW","PANW",
             "MRK","DHR","ISRG","SYK","VRTX","REGN","NKE","TJX","COP","EOG","NEM",
             # added: verified live against SPUS's published holdings CSV (sp-funds.com),
             # ordered roughly by SPUS weight — see SCREENS for per-fund confirmation.
             "TSLA","ABBV","CSCO","GEV","KLAC","TMO","SNDK","ANET","CRWD","ADI",
             "FTNT","EMR","CDNS","ITW","CTAS"]

# TSX tickers use the exchange's own dot notation for share classes (e.g. "TECK.B");
# generate_report.py converts the dot to a dash before appending ".TO" for the Yahoo
# Finance lookup (Yahoo's symbol is "TECK-B.TO", not "TECK.B.TO" — verified live).
CA_STOCKS = ["AEM","CCO","SHOP","DSG","CSU","CNR","CP","CNQ","SU","CVE","WCN","STN","IMO",
             # added: hand-screened from the S&P/TSX Composite for permissible business
             # lines — mining/royalty, industrials, software, autos/manufacturing,
             # E&P energy. Deliberately excludes, as a category, banks/insurers/asset
             # managers, REITs, regulated utilities, telecoms and oil & gas pipelines —
             # same profile the original 13 already follow. None of these carry an
             # index-fund Shariah screen (SPUS/HLAL are US-domiciled and structurally
             # can't hold TSX names) — business-line judgement only; ratios are still
             # scored live like everything else.
             "ABX","AGI","FNV","K","TECK.B","WPM","LUN","FM",              # mining/royalty
             "CAE","ATRL","GFL","TFII","TIH","MDA","RBA","CJT",            # industrials
             "GIB.A","OTEX","KXS","CLS","BB","LSPD",                       # software/tech
             "CTC.A","CCL.B","GIL","MG","LNR","NFI","DOO",                 # manufacturing/consumer
             "SAP","EMP.A","NWC",                                         # food (no embedded lender; see QUESTIONABLE)
             "TOU","ARX","VET","WCP","NXE"]                                # E&P energy incl. uranium

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
# The 15 added 2026-08-25: spus=True confirmed against SPUS's full published holdings
# CSV (220 names). hlal=True confirmed only for the four that appeared in HLAL's own
# public top-25 (wahedinvest.com blocks automated fetches, so the rest of HLAL's ~213
# holdings couldn't be checked) — the other eleven default to False until re-verified;
# they may well be held, this just isn't confirmed one way or the other.
for _t in ("TSLA","CSCO","GEV","KLAC"):
    SCREENS[_t] = {"spus": True, "hlal": True}
for _t in ("ABBV","TMO","SNDK","ANET","CRWD","ADI","FTNT","EMR","CDNS","ITW","CTAS"):
    SCREENS[_t] = {"spus": True, "hlal": False}
del _t
SCREENS_ASOF = "2026-08-25"

# Names deliberately excluded from the universe.
EXCLUDED = ["MCD","CMG","DE","HON","GE","LMT","RTX","TMUS","DIS","AMGN",
            "MFI"]        # Maple Leaf Foods — major Canadian pork processor
# Screens disagree or a name carries an embedded conventional-finance business line
# worth a second look before treating it as a clean buy.
QUESTIONABLE = ["COST","WMT","NFLX","SBUX","INTU","CAT",
                "ATD","L","MRU","WN","DOL","PBH"]   # CA: convenience/grocery retail
                                                     # with lottery/tobacco exposure or
                                                     # an embedded financial-services arm
                                                     # (e.g. Loblaw/PC Financial)

# Documented data facts, so the report can distinguish "missing" from "genuinely absent".
NO_DEBT = {"ISRG"}          # D/E absent because there is no meaningful debt
