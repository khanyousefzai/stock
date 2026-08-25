# -*- coding: utf-8 -*-
"""Renders one day's report page from scored rows."""
import html
from report_css import REPORT_CSS
from scoring import cls_pe, cls_pb, cls_roe, cls_de, cls_cr, commentary
from universe import SCREENS, SCREENS_ASOF, EXCLUDED, QUESTIONABLE, NO_DEBT

STRIPE = {"Strong Buy":"s-buy","Buy":"s-buy","Hold":"s-hold","Wait":"s-wait","Skip":"s-wait"}
BADGE  = {"Strong Buy":"b-sbuy","Buy":"b-buy","Hold":"b-hold","Wait":"b-wait","Skip":"b-skip"}


def e(s): return html.escape(str(s))

def n(v, d=2, suf=""):
    if v is None: return '<span class="na">n/a</span>'
    return ("%." + str(d) + "f") % v + suf

def pct(v, d=2):
    if v is None: return '<span class="na">n/a</span>'
    return "%+.*f%%" % (d, v)

def money(v, cur="$", d=2):
    if v is None: return '<span class="na">n/a</span>'
    return cur + format(v, ",.%df" % d)

def chg_cls(v):
    if v is None: return "na"
    return "up" if v > 0 else ("down" if v < 0 else "flat")

def ratio_td(v, cls, d=2, suf=""):
    if v is None: return '<td class="num"><span class="na">n/a</span></td>'
    return '<td class="num"><span class="rv %s">%s</span></td>' % (
        cls, ("%." + str(d) + "f") % v + suf)

def dash(r):
    items = [("P/E", n(r.get("pe")), cls_pe(r.get("pe"))),
             ("P/B", n(r.get("pb")), cls_pb(r.get("pb"))),
             ("ROE", n(r.get("roe_pct"), 1, "%"), cls_roe(r.get("roe_pct"))),
             ("D/E", n(r.get("de")), cls_de(r.get("de"))),
             ("Curr", n(r.get("current_ratio")), cls_cr(r.get("current_ratio")))]
    out = ['<div class="dash">']
    for lab, val, c in items:
        out.append('<div class="dcell"><span class="dlab">%s</span>'
                   '<span class="dval %s">%s</span></div>' % (lab, c, val))
    return "".join(out) + "</div>"

def screen_of(t):
    s = SCREENS.get(t)
    if not s: return "unknown"
    if s["spus"] and s["hlal"]: return "SPUS+HLAL"
    if s["spus"]: return "SPUS only"
    if s["hlal"]: return "HLAL only"
    return "Neither (non-US domicile)"

def upside_td(r, cur="$"):
    if r.get("analyst_target") is None:
        return '<td class="num"><span class="na">no target</span></td>'
    c = "up" if r["upside"] > 0 else "down"
    return ('<td class="num"><span class="tgt">%s</span>'
            '<span class="ups %s">%+.1f%%</span></td>'
            % (money(r["analyst_target"], cur), c, r["upside"]))


RATIO_CARDS = [
 ("P/E","Price to Earnings","What you pay for each dollar the company earns. A P/E of 20 means twenty years of current earnings to pay back the share price. Low can mean cheap &mdash; or that earnings are expected to fall.",
  [("g","below 20","cheap"),("a","20 &ndash; 50","premium"),("r","above 50","expensive")]),
 ("P/B","Price to Book","Share price against the accounting value of net assets. Useful for banks and miners; misleading for asset-light firms and any company that has bought back a lot of stock, which shrinks book equity toward zero.",
  [("g","below 3","asset-backed"),("a","3 &ndash; 15","typical"),("r","above 15","thin")]),
 ("ROE","Return on Equity","Profit generated per dollar of shareholder capital. The best quick measure of business quality &mdash; but check debt alongside it, because leverage inflates ROE without improving the business.",
  [("g","above 30%","excellent"),("a","10 &ndash; 30%","solid"),("r","below 10%","weak")]),
 ("D/E","Debt to Equity","Borrowings against shareholder capital. Central to Shariah screening, though the AAOIFI test measures debt against <em>market capitalisation</em> with a 33% ceiling &mdash; not against book equity as shown here.",
  [("g","below 0.5","low"),("a","0.5 &ndash; 1.5","moderate"),("r","above 1.5","leveraged")]),
 ("Curr","Current Ratio","Short-term assets against short-term bills. Below 1.0 means the company owes more within a year than it holds in liquid assets &mdash; survivable for a cash-generative giant, dangerous for anyone else.",
  [("g","above 2.0","strong"),("a","1.0 &ndash; 2.0","adequate"),("r","below 1.0","tight")]),
]


def render(us, ca, funds, meta, tweets=None):
    """us/ca: scored rows sorted by score desc. funds: fund rows. meta: dict.
    tweets: optional list from investor_tweets.fetch(), or None/[] to omit the section."""
    P, A = [], None
    A = P.append
    A(REPORT_CSS)

    moves = [r["day_change_pct"] for r in us if r.get("day_change_pct") is not None]
    avg = sum(moves) / len(moves) if moves else None
    counts = {k: len([r for r in us + ca if r["verdict"] == k])
              for k in ["Strong Buy", "Buy", "Hold", "Wait", "Skip"]}
    top = us[0] if us else None

    # ---------- hero ----------
    A('<div class="hero"><canvas id="stars"></canvas><div class="hero-in">'
      '<div class="brand"><span class="eyebrow">Daily Shariah-Screened Equity Review</span>'
      '<h1>Halal Market Ledger</h1>'
      '<p class="sub">Sixty Shariah-screened securities &mdash; 35 US stocks, 13 TSX listings and 12 halal '
      'funds &mdash; ranked on a single 105-point value-and-quality model.</p></div>'
      '<div class="stamp"><span class="live">%s</span><span class="big">%s</span>'
      '<span class="sm">Quotes captured %s</span>'
      '<span class="sm">Source: Yahoo Finance &middot; issuer holdings files</span></div>'
      '</div></div>' % (e(meta["status"]), e(meta["label"]), e(meta["captured"])))

    A('<nav><div class="nav-in">'
      '<a href="#a"><span class="k">A</span>Ratios &amp; Method</a>'
      '<a href="#b"><span class="k">B</span>US Overview</a>'
      '<a href="#c"><span class="k">C</span>US Financial Health</a>'
      '<a href="#d"><span class="k">D</span>Top 5 US Picks</a>'
      '<a href="#e"><span class="k">E</span>All 35 US Names</a>'
      '<a href="#f"><span class="k">F</span>Canada</a>'
      '<a href="#g"><span class="k">G</span>Halal Funds</a>'
      '<a href="#h"><span class="k">H</span>Notes &amp; Watchpoints</a>'
      + ('<a href="#i"><span class="k">I</span>Investor Chatter</a>' if tweets else '') +
      '</div></nav>')

    A('<div class="wrap">')
    A('<div class="strip">')
    if top:
        A('<div class="sc hi"><span class="l">Top pick</span><span class="v">%s</span>'
          '<span class="m">score %.1f%s</span></div>'
          % (e(top["ticker"]), top["score"],
             " &middot; %+.0f%% upside" % top["upside"] if top.get("upside") else ""))
    for lab, key, note in [("Strong Buy","Strong Buy","of 48 stocks"),
                           ("Buy","Buy","score 65&ndash;79"),
                           ("Hold","Hold","score 48&ndash;64")]:
        A('<div class="sc"><span class="l">%s</span><span class="v">%d</span>'
          '<span class="m">%s</span></div>' % (lab, counts[key], note))
    A('<div class="sc"><span class="l">Wait / Skip</span><span class="v">%d</span>'
      '<span class="m">below 48 or capped</span></div>'
      % (counts["Wait"] + counts["Skip"]))
    if avg is not None:
        A('<div class="sc"><span class="l">US avg day move</span><span class="v %s">%+.2f%%</span>'
          '<span class="m">%d names</span></div>' % (chg_cls(avg), avg, len(moves)))
    A('</div>')

    # ---------- A ----------
    A('<section id="a"><div class="sec-head"><span class="sec-key">A</span>'
      '<h2>How to read the ratios</h2>'
      '<span class="sec-note">Colour bands apply to every table and card below</span></div>')
    A('<p class="lede">Five ratios drive everything here. Each is colour-coded the same way wherever it '
      'appears: <span class="rv g">jade</span> is healthy, <span class="rv a">amber</span> is acceptable '
      'but worth watching, <span class="rv r">red</span> is a flag that needs a reason.</p>')
    A('<div class="rgrid">')
    for k, full, desc, bands in RATIO_CARDS:
        A('<div class="rcard"><h3>%s</h3><span class="full">%s</span><p>%s</p><div class="bands">'
          % (k, full, desc))
        for c, rng, lab in bands:
            A('<div class="bd"><span class="sw %s"></span><span class="txt">%s</span>'
              '<span class="txt" style="color:var(--ink-3);margin-left:auto">%s</span></div>'
              % (c, rng, lab))
        A('</div></div>')
    A('</div>')
    A('''<div class="method"><h3>The 105-point score</h3>
<p>Every one of the 48 stocks is scored identically. Six components are graded on sliding scales &mdash; no
arbitrary cut-offs inside a component &mdash; and summed. The weighting deliberately puts more on the balance
sheet (D/E plus current ratio = 35 points) than on the analyst target (26 points), because forecasts are
opinions and the balance sheet is a fact.</p>
<div class="mgrid">
<div class="mi"><div class="p">26</div><div class="n2">Analyst upside</div></div>
<div class="mi"><div class="p">20</div><div class="n2">P/E valuation</div></div>
<div class="mi"><div class="p">20</div><div class="n2">Debt / equity</div></div>
<div class="mi"><div class="p">20</div><div class="n2">Return on equity</div></div>
<div class="mi"><div class="p">15</div><div class="n2">Current ratio</div></div>
<div class="mi"><div class="p">5</div><div class="n2">Day momentum</div></div>
</div>
<div class="bandrow">
<span class="badge b-sbuy">Strong Buy&nbsp; 80+</span><span class="badge b-buy">Buy&nbsp; 65&ndash;79</span>
<span class="badge b-hold">Hold&nbsp; 48&ndash;64</span><span class="badge b-wait">Wait&nbsp; 36&ndash;47</span>
<span class="badge b-skip">Skip&nbsp; under 36</span></div>
<div class="guard"><strong style="font-size:13px">Guardrails that override the score</strong>
<p style="margin:4px 0 0;font-size:12.5px">A high score cannot buy its way past these.</p>
<ul><li><b>D/E above 3.0</b> &rarr; capped at Wait</li><li><b>P/E above 150</b> &rarr; capped at Wait</li>
<li><b>Target below price</b> &rarr; capped at Hold</li><li><b>Upside under 3%</b> &rarr; capped at Hold</li>
<li><b>No analyst target</b> &rarr; capped at Hold</li></ul></div></div>''')
    A('</section>')

    # ---------- B ----------
    A('<section id="b"><div class="sec-head"><span class="sec-key">B</span><h2>US overview</h2>'
      '<span class="sec-note">%d names, ranked by score</span></div>' % len(us))
    A('<p class="lede">The <em>Screen</em> column records which Shariah index holds the stock, from the '
      'issuers\' published holdings files (as of %s). <code>SPUS+HLAL</code> means both screens clear it.</p>'
      % e(SCREENS_ASOF))
    A('<div class="tw"><table><thead><tr><th>Stock</th><th>Sector</th><th class="num">Price</th>'
      '<th class="num">Day</th><th class="num">Target / Upside</th><th>Screen</th><th>Verdict</th>'
      '<th class="num">Score</th></tr></thead><tbody>')
    for r in us:
        sc = screen_of(r["ticker"])
        A('<tr class="%s"><td class="nm"><span class="co">%s</span><span class="tk">%s</span></td>'
          '<td class="sect">%s</td><td class="num">%s</td><td class="num %s">%s</td>%s'
          '<td><span class="scr %s">%s</span></td><td><span class="badge %s">%s</span></td>'
          '<td class="num sco">%.1f</td></tr>'
          % (STRIPE[r["verdict"]], e(r["name"]), e(r["ticker"]), e(r.get("sector", "")),
             money(r["price"]), chg_cls(r.get("day_change_pct")), pct(r.get("day_change_pct")),
             upside_td(r), "both" if sc == "SPUS+HLAL" else "", e(sc),
             BADGE[r["verdict"]], e(r["verdict"]), r["score"]))
    A('</tbody></table></div></section>')

    # ---------- C ----------
    A('<section id="c"><div class="sec-head"><span class="sec-key">C</span>'
      '<h2>US financial health</h2><span class="sec-note">Same order, ratios only</span></div>')
    A('<p class="lede">Read the colours across a row: a line of jade is a genuinely sound company; a mix of '
      'red and amber means the score is carried by the analyst target rather than by the business.</p>')
    A('<div class="tw"><table><thead><tr><th>Stock</th><th class="num">P/E</th><th class="num">P/B</th>'
      '<th class="num">ROE</th><th class="num">D/E</th><th class="num">Current</th>'
      '<th class="num">Score</th></tr></thead><tbody>')
    for r in us:
        A('<tr class="%s"><td class="nm"><span class="co">%s</span><span class="tk">%s</span></td>'
          '%s%s%s%s%s<td class="num sco">%.1f</td></tr>'
          % (STRIPE[r["verdict"]], e(r["name"]), e(r["ticker"]),
             ratio_td(r.get("pe"), cls_pe(r.get("pe"))),
             ratio_td(r.get("pb"), cls_pb(r.get("pb"))),
             ratio_td(r.get("roe_pct"), cls_roe(r.get("roe_pct")), 1, "%"),
             ratio_td(r.get("de"), cls_de(r.get("de"))),
             ratio_td(r.get("current_ratio"), cls_cr(r.get("current_ratio"))), r["score"]))
    A('</tbody></table></div>')
    A('<p class="lede" style="margin-top:14px;font-size:13px">Where price-to-book runs above 20 and return '
      'on equity above 100%, those are the same fact seen twice &mdash; years of buybacks shrinking book '
      'equity toward zero inflate both. Neither is evidence of exceptional asset efficiency.</p></section>')

    # ---------- D ----------
    clean = [r for r in us if not r["guardrails"]][:5]
    A('<section id="d"><div class="sec-head"><span class="sec-key">D</span><h2>Top 5 US picks</h2>'
      '<span class="sec-note">Highest scores clearing every guardrail</span></div>')
    A('<div class="picks">')
    for i, r in enumerate(clean, 1):
        A('<div class="pick"><div class="rank">%d</div><div>' % i)
        A('<div class="pick-h"><span class="nm2">%s</span><span class="tk2">%s</span>'
          '<span class="badge %s">%s</span><span class="scr" style="color:var(--jade)">%s</span></div>'
          % (e(r["name"]), e(r["ticker"]), BADGE[r["verdict"]], e(r["verdict"]),
             e(screen_of(r["ticker"]))))
        A('<div class="pline"><span class="px">%s</span><span class="%s">%s today</span>'
          '<span style="color:var(--ink-3)">mkt cap %s</span>'
          '<span style="color:var(--ink-3)">target %s &middot; <span class="up">%+.1f%%</span></span></div>'
          % (money(r["price"]), chg_cls(r.get("day_change_pct")), pct(r.get("day_change_pct")),
             e(r.get("market_cap", "n/a")), money(r["analyst_target"]), r["upside"]))
        A(dash(r))
        A('<p class="an">%s</p>' % e(commentary(r)))
        c = r["components"]
        A('<div class="pfoot"><span>score <b>%.1f</b> / 105</span><span>upside <b>%.1f</b>/26</span>'
          '<span>P/E <b>%.1f</b>/20</span><span>D/E <b>%.1f</b>/20</span><span>ROE <b>%.1f</b>/20</span>'
          '<span>liquidity <b>%.1f</b>/15</span><span>momentum <b>%.1f</b>/5</span></div>'
          % (r["score"], c["upside"], c["pe"], c["de"], c["roe"], c["cr"], c["mom"]))
        A('</div></div>')
    A('</div></section>')

    # ---------- E / F cards ----------
    def card(r, cur="$", show_screen=True):
        o = ['<div class="card %s">' % STRIPE[r["verdict"]]]
        o.append('<div class="chead"><div><div class="cn">%s</div>'
                 '<span class="ct">%s &middot; %s</span></div>'
                 '<span class="badge %s">%s</span></div>'
                 % (e(r["name"]), e(r["ticker"]), e(r.get("sector", "")),
                    BADGE[r["verdict"]], e(r["verdict"])))
        o.append('<div class="cprice"><span class="p1">%s</span><span class="%s">%s</span>'
                 '<span class="mc">%s</span></div>'
                 % (money(r["price"], cur), chg_cls(r.get("day_change_pct")),
                    pct(r.get("day_change_pct")), e(r.get("market_cap", "n/a"))))
        o.append(dash(r))
        o.append('<p class="an">%s</p>' % e(commentary(r)))
        if r["guardrails"]:
            o.append('<div class="gflag">Guardrail: %s</div>' % e(" · ".join(r["guardrails"])))
        tg = money(r["analyst_target"], cur) if r.get("analyst_target") is not None \
             else '<span class="na">none</span>'
        up = ('<span class="%s">%+.1f%%</span>' % ("up" if r["upside"] > 0 else "down", r["upside"])) \
             if r.get("upside") is not None else '<span class="na">n/a</span>'
        scr = ('<span>screen <b>%s</b></span>' % e(screen_of(r["ticker"]))) if show_screen else ""
        o.append('<div class="cfoot"><span>target <b>%s</b></span><span>upside %s</span>%s'
                 '<span>score <b>%.1f</b></span></div>' % (tg, up, scr, r["score"]))
        return "".join(o) + "</div>"

    A('<section id="e"><div class="sec-head"><span class="sec-key">E</span>'
      '<h2>All %d US names</h2><span class="sec-note">Score order &middot; jade = buy, grey = hold, '
      'red = wait or skip</span></div><div class="cards">' % len(us))
    for r in us:
        A(card(r))
    A('</div></section>')

    # ---------- F ----------
    A('<section id="f"><div class="sec-head"><span class="sec-key">F</span><h2>Canada &mdash; TSX</h2>'
      '<span class="sec-note">%d listings &middot; figures in C$</span></div>' % len(ca))
    A('<p class="lede">Identical scoring, prices in Canadian dollars. One caveat for this whole section: '
      'SPUS and HLAL track US-domiciled universes and structurally cannot hold TSX listings, so '
      '<strong>no index screen has vetted these names</strong>. Their business lines are all permissible, '
      'but the financial-ratio and purification screens need checking individually.</p>')
    A('<div class="tw"><table><thead><tr><th>Stock</th><th>Sector</th><th class="num">Price (C$)</th>'
      '<th class="num">Day</th><th class="num">Target / Upside</th><th>Verdict</th>'
      '<th class="num">Score</th></tr></thead><tbody>')
    for r in ca:
        A('<tr class="%s"><td class="nm"><span class="co">%s</span><span class="tk">%s.TO</span></td>'
          '<td class="sect">%s</td><td class="num">%s</td><td class="num %s">%s</td>%s'
          '<td><span class="badge %s">%s</span></td><td class="num sco">%.1f</td></tr>'
          % (STRIPE[r["verdict"]], e(r["name"]), e(r["ticker"]), e(r.get("sector", "")),
             money(r["price"], "C$"), chg_cls(r.get("day_change_pct")),
             pct(r.get("day_change_pct")), upside_td(r, "C$"),
             BADGE[r["verdict"]], e(r["verdict"]), r["score"]))
    A('</tbody></table></div>')
    A('<h3 style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:23px;font-weight:600;'
      'margin:26px 0 10px">Canadian financial health</h3>')
    A('<div class="tw"><table><thead><tr><th>Stock</th><th class="num">P/E</th><th class="num">P/B</th>'
      '<th class="num">ROE</th><th class="num">D/E</th><th class="num">Current</th>'
      '<th class="num">Score</th></tr></thead><tbody>')
    for r in ca:
        A('<tr class="%s"><td class="nm"><span class="co">%s</span><span class="tk">%s.TO</span></td>'
          '%s%s%s%s%s<td class="num sco">%.1f</td></tr>'
          % (STRIPE[r["verdict"]], e(r["name"]), e(r["ticker"]),
             ratio_td(r.get("pe"), cls_pe(r.get("pe"))),
             ratio_td(r.get("pb"), cls_pb(r.get("pb"))),
             ratio_td(r.get("roe_pct"), cls_roe(r.get("roe_pct")), 1, "%"),
             ratio_td(r.get("de"), cls_de(r.get("de"))),
             ratio_td(r.get("current_ratio"), cls_cr(r.get("current_ratio"))), r["score"]))
    A('</tbody></table></div>')
    A('<h3 style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:23px;font-weight:600;'
      'margin:30px 0 10px">All %d Canadian names</h3><div class="cards">' % len(ca))
    for r in ca:
        A(card(r, "C$", show_screen=False))
    A('</div></section>')

    # ---------- G ----------
    A('<section id="g"><div class="sec-head"><span class="sec-key">G</span>'
      '<h2>Halal ETFs &amp; funds</h2><span class="sec-note">%d vehicles</span></div>' % len(funds))
    A('<p class="lede">For anyone who would rather own the screen than pick within it. The US index ETFs '
      'are top-heavy, SPSK is the only fixed-income option, and the Amana mutual funds price once daily '
      'at NAV rather than trading intraday.</p>')
    A('<div class="tw"><table style="min-width:980px"><thead><tr><th>Fund</th><th>Type</th>'
      '<th class="num">Price</th><th class="num">Day</th><th class="num">Expense</th>'
      '<th class="num">AUM</th><th class="num">Holdings</th><th class="num">Yield</th>'
      '<th class="num">YTD</th><th>Focus</th></tr></thead><tbody>')
    for f in funds:
        cur = "C$" if f.get("currency") == "CAD" else "$"
        A('<tr class="s-hold"><td class="nm"><span class="co">%s</span><span class="tk">%s</span></td>'
          '<td class="sect">%s</td><td class="num">%s</td><td class="num %s">%s</td>'
          '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
          '<td class="num">%s</td><td class="num">%s</td><td class="sect">%s</td></tr>'
          % (e(f["name"]), e(f["ticker"]), e(f["type"]), money(f.get("price"), cur),
             chg_cls(f.get("day_change_pct")), pct(f.get("day_change_pct")),
             n(f.get("expense_ratio"), 2, "%"), e(f.get("aum", "n/a")),
             e(f.get("holdings_count") or "n/a"), n(f.get("dividend_yield"), 2, "%"),
             n(f.get("ytd_return"), 2, "%"), e(f.get("focus", ""))))
    A('</tbody></table></div>')
    A('<div class="fcards" style="margin-top:22px">')
    for f in funds:
        cur = "C$" if f.get("currency") == "CAD" else "$"
        A('<div class="card s-hold"><div class="chead"><div><div class="cn">%s</div>'
          '<span class="ct">%s &middot; %s</span></div></div>' % (e(f["name"]), e(f["ticker"]), e(f["type"])))
        A('<div class="cprice"><span class="p1">%s</span><span class="%s">%s</span>'
          '<span class="mc">%s AUM</span></div>'
          % (money(f.get("price"), cur), chg_cls(f.get("day_change_pct")),
             pct(f.get("day_change_pct")), e(f.get("aum", "n/a"))))
        A('<div class="dash" style="grid-template-columns:repeat(4,1fr)">')
        for lab, val in [("Expense", n(f.get("expense_ratio"), 2, "%")),
                         ("Holdings", e(f.get("holdings_count") or "n/a")),
                         ("Yield", n(f.get("dividend_yield"), 2, "%")),
                         ("YTD", n(f.get("ytd_return"), 2, "%"))]:
            A('<div class="dcell"><span class="dlab">%s</span><span class="dval">%s</span></div>'
              % (lab, val))
        A('</div>')
        A('<p class="an">%s A %s tracking %s.</p>'
          % (e(f["name"]), f["type"].lower(), e(f.get("focus", "").lower())))
        if f.get("top_holdings"):
            A('<div class="hlab">Top 3 holdings</div><div class="hold">')
            for h in f["top_holdings"][:3]:
                A('<div class="hrow"><span>%s</span></div>' % e(h))
            A('</div>')
        A('<div class="cfoot"><span>currency <b>%s</b></span></div></div>' % e(f.get("currency", "USD")))
    A('</div></section>')

    # ---------- H ----------
    gaps = [r for r in us + ca if r.get("pe") is None or r.get("roe_pct") is None
            or r.get("current_ratio") is None or r.get("analyst_target") is None]
    extreme = [r for r in us + ca
               if (r.get("pe") or 0) > 100 or (r.get("de") or 0) > 3 or (r.get("pb") or 0) > 20]
    A('<section id="h"><div class="sec-head"><span class="sec-key">H</span>'
      '<h2>Notes &amp; watchpoints</h2>'
      '<span class="sec-note">Read before acting on anything above</span></div><div class="ngrid">')

    ups = sorted([r for r in us if r.get("day_change_pct") is not None],
                 key=lambda r: r["day_change_pct"], reverse=True)
    A('<div class="ncard"><h3>Session movers</h3><ul>')
    for r in ups[:4]:
        A('<li><strong>%s</strong> %+.2f%% &mdash; %s</li>'
          % (e(r["ticker"]), r["day_change_pct"], e(r.get("sector", ""))))
    A('</ul><p style="margin-top:8px">Weakest:</p><ul>')
    for r in ups[-4:]:
        A('<li><strong>%s</strong> %+.2f%% &mdash; %s</li>'
          % (e(r["ticker"]), r["day_change_pct"], e(r.get("sector", ""))))
    A('</ul></div>')

    A('<div class="ncard"><h3>Shariah compliance notes</h3>'
      '<p><strong>The screens genuinely disagree.</strong> SPUS follows the S&amp;P 500 Sharia methodology '
      'and HLAL the FTSE USA Shariah index. FTSE measures debt against total assets while S&amp;P measures '
      'against market cap, so a name can clear one and fail the other &mdash; the Screen column in section B '
      'records which.</p>'
      '<p><strong>Debt is screened against market capitalisation</strong> under AAOIFI, with a 33% ceiling '
      '&mdash; not against book equity. A high book D/E in section C is therefore not automatically '
      'disqualifying. Zoya is looser than either index screen.</p>'
      '<p><strong>Purification.</strong> Even compliant companies earn incidental interest income. The '
      'standard practice is to calculate the non-compliant portion of dividends received and donate it. '
      'Fund providers publish annual purification ratios; for direct holdings you calculate it yourself.</p>'
      '<p><strong>Excluded as non-compliant:</strong> ' + ", ".join(EXCLUDED) + '. '
      '<strong>Questionable</strong> &mdash; screens disagree, decide for yourself: '
      + ", ".join(QUESTIONABLE) + '.</p></div>')

    A('<div class="ncard dq"><h3>Data quality &mdash; this run</h3>')
    A('<p>Every figure comes from Yahoo Finance at %s. Nothing is estimated or filled from memory: a field '
      'that could not be read shows <em>n/a</em> and is scored neutrally.</p>' % e(meta["captured"]))
    if gaps:
        A('<p><strong>Incomplete rows (%d):</strong> %s. Their scores lean on neutral placeholders and '
          'should be read as partly unassessed.</p>'
          % (len(gaps), ", ".join(e(r["ticker"]) for r in gaps[:14])))
    else:
        A('<p><strong>No data gaps.</strong> All 48 stocks returned a complete ratio set.</p>')
    if extreme:
        A('<p><strong>Extreme but verified:</strong> %s.</p>'
          % ", ".join("%s (P/E %s, D/E %s, P/B %s)"
                      % (e(r["ticker"]), n(r.get("pe"), 1), n(r.get("de")), n(r.get("pb"), 1))
                      for r in extreme[:8]))
    if meta.get("failures"):
        A('<p><strong>Fetch failures (%d):</strong> %s. These are omitted from the tables entirely rather '
          'than shown with invented values.</p>'
          % (len(meta["failures"]), ", ".join(e(x) for x in meta["failures"])))
    A('<p><strong>Screen membership</strong> is from the issuers\' own holdings files, last refreshed %s. '
      'Re-check it periodically &mdash; index constituents change.</p>' % e(SCREENS_ASOF))
    A('</div></div>')

    # ---------- I ----------
    if tweets:
        A('<section id="i"><div class="sec-head"><span class="sec-key">I</span>'
          '<h2>Investor chatter</h2>'
          '<span class="sec-note">Recent posts from watched accounts mentioning a ticker in this universe</span></div>')
        A('<p class="lede">A mention here is <strong>not confirmation of a trade</strong> &mdash; these '
          'accounts comment publicly far more often than they disclose actual positions, and a cashtag in a '
          'post can be praise, criticism, or a joke. Read it as chatter to follow up on, not a signal.</p>')
        A('<div class="ngrid">')
        for tw in tweets:
            A('<div class="ncard"><h3>%s <span style="color:var(--ink-3);font-weight:400">&middot; %s</span></h3>'
              '<p>%s</p><p style="margin-top:6px;font-size:12.5px">'
              '<span class="badge b-buy">%s</span> &middot; '
              '<a href="%s" style="color:var(--jade)">view post</a></p></div>'
              % (e(tw["name"]), e(tw["firm"]), e(tw["text"]),
                 " &middot; ".join(e(t) for t in tw["tickers"]), e(tw["url"])))
        A('</div></section>')

    A('<div class="disc"><b>Not investment advice.</b> This is an automated daily screen, not a '
      'recommendation to buy or sell anything. The scores are the output of a fixed formula applied to '
      'publicly reported ratios &mdash; they encode no view on business quality, management, competitive '
      'position, or any development not visible in these numbers. Analyst targets are opinions with a poor '
      'forecasting record and carry a quarter of the weight. Prices are %s and were moving as this was '
      'generated; verify before you trade. Shariah compliance is a personal religious obligation &mdash; '
      'index screens disagree with one another, and none substitutes for your own scholarship or a '
      'qualified advisor. Do your own research.</div>' % e(meta["captured"]))
    A('<footer><span>Halal Market Ledger &middot; %s</span>'
      '<span>%d securities &middot; %d scored</span></footer>'
      % (e(meta["label"]), len(us) + len(ca) + len(funds), len(us) + len(ca)))
    A('</div>')
    return "\n".join(P)
