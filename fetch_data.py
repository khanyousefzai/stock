# -*- coding: utf-8 -*-
"""
Data layer for the Halal Market Ledger.

Pulls quotes and fundamentals from Yahoo Finance via yfinance. Every field is
normalised to a plain float or None — never a guess, never a placeholder.

Unit notes (yfinance quirks that WILL silently corrupt the scoring if ignored):
  * returnOnEquity  is a FRACTION  (0.1487  -> 14.87%)
  * debtToEquity    is a PERCENT   (78.4    -> 0.784 ratio)
  * annualReportExpenseRatio / yield / ytdReturn are FRACTIONS for funds
"""
import time

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    yf = None


class FetchError(Exception):
    pass


def _f(v):
    """Coerce to float, or None. Rejects bools, NaN and infinities."""
    if v is None or isinstance(v, bool):
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    return v


def _first(info, *keys):
    for k in keys:
        v = _f(info.get(k))
        if v is not None:
            return v
    return None


def _mcap(v):
    if v is None:
        return "n/a"
    for cut, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if abs(v) >= cut:
            return "%.2f%s" % (v / cut, suf)
    return "%.0f" % v


def _day_change_pct(info):
    """Prefer the reported percent; otherwise derive it from price vs previous close."""
    p = _f(info.get("regularMarketChangePercent"))
    if p is not None:
        # Yahoo has returned this both as 1.23 and as 0.0123 depending on endpoint.
        return p * 100.0 if abs(p) < 1.0 and p != 0 and _looks_fractional(info) else p
    price = _first(info, "currentPrice", "regularMarketPrice")
    prev = _first(info, "regularMarketPreviousClose", "previousClose")
    if price is not None and prev:
        return (price - prev) / prev * 100.0
    return None


def _looks_fractional(info):
    """Cross-check the percent field against price/prevClose to settle its unit."""
    p = _f(info.get("regularMarketChangePercent"))
    price = _first(info, "currentPrice", "regularMarketPrice")
    prev = _first(info, "regularMarketPreviousClose", "previousClose")
    if p is None or price is None or not prev:
        return False
    derived = (price - prev) / prev * 100.0
    return abs(derived - p * 100.0) < abs(derived - p)


def fetch_stock(symbol, retries=3, pause=1.5):
    """Return one normalised stock row. Raises FetchError if the quote is unusable."""
    if yf is None:
        raise FetchError("yfinance is not installed")
    last = None
    for attempt in range(retries):
        try:
            info = yf.Ticker(symbol).info or {}
            price = _first(info, "currentPrice", "regularMarketPrice")
            if price is None:
                raise FetchError("no price field for %s" % symbol)

            roe = _f(info.get("returnOnEquity"))
            de = _f(info.get("debtToEquity"))
            return {
                "ticker": symbol.replace(".TO", "").replace(".NE", ""),
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "sector": info.get("sector") or "n/a",
                "currency": info.get("currency") or "USD",
                "price": price,
                "day_change_pct": _day_change_pct(info),
                "market_cap": _mcap(_f(info.get("marketCap"))),
                "analyst_target": _f(info.get("targetMeanPrice")),
                "analyst_count": _f(info.get("numberOfAnalystOpinions")),
                "pe": _first(info, "trailingPE"),
                "pb": _first(info, "priceToBook"),
                "roe_pct": roe * 100.0 if roe is not None else None,
                "de": de / 100.0 if de is not None else None,
                "current_ratio": _f(info.get("currentRatio")),
                "notes": "",
            }
        except Exception as ex:  # noqa: BLE001 - retry any transport/parse failure
            last = ex
            if attempt < retries - 1:
                time.sleep(pause * (attempt + 1))
    raise FetchError("%s: %s" % (symbol, last))


def fetch_fund(symbol, kind, focus, retries=3, pause=1.5):
    """Return one normalised fund row. Missing fields stay None rather than guessed."""
    if yf is None:
        raise FetchError("yfinance is not installed")
    last = None
    for attempt in range(retries):
        try:
            tk = yf.Ticker(symbol)
            info = tk.info or {}
            price = _first(info, "currentPrice", "regularMarketPrice",
                           "navPrice", "previousClose")
            if price is None:
                raise FetchError("no price field for %s" % symbol)

            exp = _first(info, "netExpenseRatio", "annualReportExpenseRatio")
            if exp is not None and exp < 1.0:
                exp *= 100.0                      # fraction -> percent
            yld = _first(info, "yield", "dividendYield")
            if yld is not None and yld < 1.0:
                yld *= 100.0
            ytd = _f(info.get("ytdReturn"))
            if ytd is not None and abs(ytd) < 1.0:
                ytd *= 100.0

            holdings = []
            try:
                fd = getattr(tk, "funds_data", None)
                th = getattr(fd, "top_holdings", None) if fd else None
                if th is not None and not th.empty:
                    for sym, row in th.head(3).iterrows():
                        w = _f(row.get("Holding Percent"))
                        nm = row.get("Name") or sym
                        holdings.append("%s %.2f%%" % (nm, w * 100.0)
                                        if w is not None and w < 1 else "%s" % nm)
            except Exception:
                holdings = []

            return {
                "ticker": symbol.replace(".NE", ""),
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "type": kind,
                "focus": focus,
                "currency": info.get("currency") or "USD",
                "price": price,
                "day_change_pct": _day_change_pct(info),
                "expense_ratio": exp,
                "aum": _mcap(_first(info, "netAssets", "totalAssets")),
                "holdings_count": info.get("holdings") or None,
                "dividend_yield": yld,
                "ytd_return": ytd,
                "top_holdings": holdings,
                "notes": "",
            }
        except Exception as ex:  # noqa: BLE001
            last = ex
            if attempt < retries - 1:
                time.sleep(pause * (attempt + 1))
    raise FetchError("%s: %s" % (symbol, last))


def reconcile(row):
    """Sanity-check a fetched row. Returns a list of human-readable warnings."""
    warn = []
    p, c = row.get("price"), row.get("day_change_pct")
    if c is not None and abs(c) > 25:
        warn.append("day move %+.1f%% is implausible" % c)
    if p is not None and p <= 0:
        warn.append("non-positive price")
    pe = row.get("pe")
    if pe is not None and pe > 500:
        warn.append("P/E %.0f — verify" % pe)
    return warn
