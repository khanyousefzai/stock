# -*- coding: utf-8 -*-
"""
13F holdings — free, official alternative/companion to investor_tweets.py.

Pulls the most recent Form 13F-HR (quarterly institutional holdings) each
watched investor filed with the SEC, and flags any reported position that
overlaps this universe. No API key, no paid plan — SEC EDGAR is public data.

This is a quarterly snapshot of confirmed holdings, not a real-time buy
signal: 13F filings can lag up to 45 days after quarter end, and a name
appearing here means "held as of the filing date", not "bought this week".
If a filer's most recent 13F reports nothing (e.g. an all-zero placeholder
filing), that simply yields no hits for them — not an error.

SEC asks every requester to send an identifying User-Agent (SEC's own
example: "Sample Company Name AdminContact@sample.com"). The default below
names this project; override with the SEC_EDGAR_USER_AGENT env var if you
want your own contact in it instead.
"""
import os
import re
from xml.etree import ElementTree as ET

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

USER_AGENT = os.environ.get(
    "SEC_EDGAR_USER_AGENT",
    "Halal Market Ledger daily-report-bot admin@halalmarketledger.local",
)
HEADERS = {"User-Agent": USER_AGENT}

# investor -> (firm, SEC CIK). CIKs are stable identifiers, resolved once
# against data.sec.gov/submissions and verified against the filer's own name.
WATCHED = [
    ("Bill Ackman", "Pershing Square Capital Management", "1336528"),
    ("Michael Burry", "Scion Asset Management", "1649339"),
    ("Chamath Palihapitiya", "Social Capital Group", "1964312"),
]

NS = {"n": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

# Tokens stripped before matching a 13F issuer name against our universe's
# company names — corporate suffixes and share-class markers, not part of
# the identity of the business.
STOPWORDS = {"INC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LLC", "PLC",
             "HOLDINGS", "HLDGS", "INTL", "INTERNATIONAL", "GROUP", "THE",
             "SA", "NV", "AG", "COM", "CLASS", "CL"}


def _norm(name):
    """Normalise a company name for matching: strip punctuation, corporate
    suffixes and single-letter share-class tokens, uppercase, collapse
    whitespace. '9310043 -> Alphabet Inc.' and 'ALPHABET INC' both -> 'ALPHABET'."""
    name = re.sub(r"[^A-Z0-9 ]", " ", (name or "").upper())
    tokens = [t for t in name.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


def _fmt_usd(v):
    for cut, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if v >= cut:
            return "$%.2f%s" % (v / cut, suf)
    return "$%.0f" % v


def _latest_13f_accession(cik):
    r = requests.get("https://data.sec.gov/submissions/CIK%s.json" % cik.zfill(10),
                      headers=HEADERS, timeout=10)
    r.raise_for_status()
    f = r.json()["filings"]["recent"]
    for form, acc, date in zip(f["form"], f["accessionNumber"], f["filingDate"]):
        if form == "13F-HR":            # skip 13F-NT (notice-only) and amendments
            return acc, date
    return None, None


def _infotable_url(cik, accession):
    """The holdings table's filename isn't standardised across filers
    ('infotable.xml' vs 'informationtable.xml', etc.) — discover it from the
    filing's own file index rather than guessing a name."""
    acc_nodash = accession.replace("-", "")
    base = "https://www.sec.gov/Archives/edgar/data/%s/%s" % (int(cik), acc_nodash)
    r = requests.get(base + "/index.json", headers=HEADERS, timeout=10)
    r.raise_for_status()
    for item in r.json()["directory"]["item"]:
        n = item["name"].lower()
        if n.endswith(".xml") and n != "primary_doc.xml":
            return base + "/" + item["name"]
    return None


def _holdings(cik, accession):
    url = _infotable_url(cik, accession)
    if not url:
        return []
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    out = []
    for it in root.findall("n:infoTable", NS):
        name = it.findtext("n:nameOfIssuer", default="", namespaces=NS)
        value = it.findtext("n:value", default="0", namespaces=NS)
        shares = it.findtext("n:shrsOrPrnAmt/n:sshPrnamt", default="0", namespaces=NS)
        try:
            out.append({"name": name, "value": float(value), "shares": float(shares)})
        except ValueError:
            continue
    return out


def fetch(universe_rows, log=None):
    """universe_rows: the scored us/ca rows from generate_report.py (each a
    dict with 'ticker' and 'name'). Returns [] on any failure — a filer's
    filing being unreachable or unparsable never blocks a report run."""
    log = log or (lambda msg: None)
    if requests is None:
        log("13F holdings: 'requests' not installed — skipping")
        return []

    lookup = {}
    for r in universe_rows:
        key = _norm(r.get("name", ""))
        if key:
            lookup[key] = r["ticker"]

    hits = []
    for investor, firm, cik in WATCHED:
        try:
            accession, filed = _latest_13f_accession(cik)
            if not accession:
                log("13F holdings: no 13F-HR on file for %s" % firm)
                continue
            for h in _holdings(cik, accession):
                ticker = lookup.get(_norm(h["name"]))
                if not ticker:
                    continue
                hits.append({
                    "investor": investor, "firm": firm, "ticker": ticker,
                    "issuer": h["name"], "value": h["value"], "shares": h["shares"],
                    "value_fmt": _fmt_usd(h["value"]), "filed": filed,
                })
        except Exception as ex:  # noqa: BLE001 — one filer failing shouldn't drop the rest
            log("13F holdings: %s failed: %s" % (firm, str(ex)[:120]))
            continue
    hits.sort(key=lambda h: -h["value"])
    return hits
