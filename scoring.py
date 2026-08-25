# -*- coding: utf-8 -*-
"""
The 105-point Halal Market Ledger score.

Six components on sliding scales (no cliff edges inside a component), summed,
then capped by guardrails a high total cannot buy past. The weighting puts more
on the balance sheet (D/E + current ratio = 35) than on the analyst target (26),
because forecasts are opinions and the balance sheet is a fact.
"""
from universe import NO_DEBT

PE_PTS  = [(0, 20), (10, 20), (20, 16), (30, 11), (50, 5), (100, 1), (200, 0)]
DE_PTS  = [(0, 20), (0.25, 19), (0.5, 17), (1.0, 13), (1.5, 9), (2.0, 6), (3.0, 2), (5.0, 0)]
ROE_PTS = [(0, 0), (5, 4), (10, 8), (15, 11), (20, 14), (30, 17), (50, 19), (80, 20)]
CR_PTS  = [(0, 0), (0.5, 2), (0.8, 5), (1.0, 7), (1.5, 11), (2.0, 14), (3.0, 15)]
MOM_PTS = [(-8, 0), (-4, 1), (-2, 2), (0, 2.5), (2, 4), (4, 5)]

ORDER = ["Strong Buy", "Buy", "Hold", "Wait", "Skip"]   # best -> worst


def interp(x, pts):
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def band(score):
    if score >= 80: return "Strong Buy"
    if score >= 65: return "Buy"
    if score >= 48: return "Hold"
    if score >= 36: return "Wait"
    return "Skip"


def cap(verdict, ceiling):
    """A verdict may be no better than `ceiling`."""
    return verdict if ORDER.index(verdict) >= ORDER.index(ceiling) else ceiling


def evaluate(row):
    """Score one stock in place-safe fashion; returns a new dict."""
    t = row["ticker"]
    price, tgt = row.get("price"), row.get("analyst_target")
    pe, roe = row.get("pe"), row.get("roe_pct")
    de, cr = row.get("de"), row.get("current_ratio")
    dc = row.get("day_change_pct")

    upside = ((tgt - price) / price * 100.0) if (tgt is not None and price) else None

    c = {}
    c["upside"] = 0.0 if upside is None else max(0.0, min(26.0, upside / 50.0 * 26.0))
    c["pe"] = 8.0 if pe is None else (0.0 if pe <= 0 else interp(pe, PE_PTS))
    if de is None:
        c["de"] = 20.0 if t in NO_DEBT else 10.0      # documented no-debt vs missing
    else:
        c["de"] = interp(de, DE_PTS)
    c["roe"] = 10.0 if roe is None else (0.0 if roe < 0 else interp(roe, ROE_PTS))
    c["cr"] = 7.5 if cr is None else interp(cr, CR_PTS)
    c["mom"] = 2.5 if dc is None else interp(dc, MOM_PTS)

    total = round(sum(c.values()), 1)
    v = band(total)
    guards = []

    if de is not None and de > 3.0:
        v = cap(v, "Wait"); guards.append("D/E above 3.0")
    if pe is not None and pe > 150:
        v = cap(v, "Wait"); guards.append("P/E above 150")
    if tgt is None:
        v = cap(v, "Hold"); guards.append("no analyst target")
    elif tgt < price:
        v = cap(v, "Hold"); guards.append("target below price")
    elif upside is not None and upside < 3:
        v = cap(v, "Hold"); guards.append("upside under 3%")

    out = dict(row)
    out.update(upside=upside, components={k: round(x, 1) for k, x in c.items()},
               score=total, raw_band=band(total), verdict=v, guardrails=guards)
    return out


# ---- colour bands (identical everywhere the ratio appears) ----
def cls_pe(v):  return "na" if v is None else ("g" if v < 20 else "a" if v <= 50 else "r")
def cls_pb(v):  return "na" if v is None else ("g" if v < 3 else "a" if v <= 15 else "r")
def cls_roe(v): return "na" if v is None else ("g" if v > 30 else "a" if v >= 10 else "r")
def cls_de(v):  return "na" if v is None else ("g" if v < 0.5 else "a" if v <= 1.5 else "r")
def cls_cr(v):  return "na" if v is None else ("g" if v > 2.0 else "a" if v >= 1.0 else "r")


# ---- commentary generated from the actual numbers ----
_PE_W  = {"g": "inexpensive", "a": "fully priced", "r": "expensive", "na": ""}
_ROE_W = {"g": "excellent", "a": "solid", "r": "weak", "na": ""}
_DE_W  = {"g": "conservatively financed", "a": "moderately geared", "r": "leveraged", "na": ""}
_CR_W  = {"g": "comfortable", "a": "adequate", "r": "tight", "na": ""}


def commentary(r):
    """3-5 sentences built strictly from this row's own figures."""
    s, t = [], r["ticker"]
    name, sector = r["name"], r.get("sector", "n/a")
    cur = "C$" if r.get("currency") == "CAD" else "$"

    dc = r.get("day_change_pct")
    move = ("up %.2f%%" % dc if dc and dc > 0 else
            "down %.2f%%" % abs(dc) if dc and dc < 0 else "flat")
    s.append("%s trades at %s%s, %s on the session." % (
        name, cur, format(r["price"], ",.2f") if r.get("price") else "n/a", move))

    pe, pb = r.get("pe"), r.get("pb")
    if pe is not None:
        bit = "It is on %.1f times trailing earnings" % pe
        if pb is not None:
            bit += " and %.2f times book" % pb
        w = _PE_W[cls_pe(pe)]
        s.append(bit + (", which reads as %s." % w if w else "."))
    elif pb is not None:
        s.append("Trailing earnings are unavailable; it trades at %.2f times book." % pb)

    roe, de, cr = r.get("roe_pct"), r.get("de"), r.get("current_ratio")
    parts = []
    if roe is not None:
        parts.append("a %s %.1f%% return on equity" % (_ROE_W[cls_roe(roe)], roe))
    if de is not None:
        parts.append("%s at %.2f debt to equity" % (_DE_W[cls_de(de)], de))
    elif t in NO_DEBT:
        parts.append("no meaningful debt at all")
    if cr is not None:
        parts.append("%s liquidity on a %.2f current ratio" % (_CR_W[cls_cr(cr)], cr))
    if parts:
        s.append("The business shows " + ", ".join(parts[:-1]) +
                 ((" and " + parts[-1]) if len(parts) > 1 else parts[-1]) + ".")

    up, tgt = r.get("upside"), r.get("analyst_target")
    if tgt is None:
        s.append("No analyst target is published, which caps the verdict at Hold "
                 "regardless of the %.1f-point score." % r["score"])
    elif up is not None:
        direction = "above" if up >= 0 else "below"
        s.append("Consensus sits at %s%s, %.1f%% %s the current price."
                 % (cur, format(tgt, ",.2f"), abs(up), direction))

    if r.get("guardrails"):
        s.append("Guardrail applied — %s — so the verdict is held at %s despite a "
                 "raw score of %.1f." % (", ".join(r["guardrails"]).lower(),
                                         r["verdict"], r["score"]))
    return " ".join(s)
