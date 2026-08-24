# Halal Market Ledger

A daily Shariah-screened equity review. Sixty securities — 35 US stocks, 13 TSX
listings and 12 halal ETFs and funds — scored each trading day on a single
105-point value-and-quality model, published as a static site.

**Live site:** `https://<your-username>.github.io/halal-market-ledger/`

---

## One-time setup

1. **Create the repository.** On GitHub, make a new *public* repo named
   `halal-market-ledger`. Don't add a README, .gitignore or licence — this
   folder already has everything.

2. **Push this folder:**

   ```bash
   cd halal-market-ledger
   git init -b main
   git add .
   git commit -m "Halal Market Ledger — initial site"
   git remote add origin https://github.com/<your-username>/halal-market-ledger.git
   git push -u origin main
   ```

3. **Turn on Pages.** Repo → **Settings** → **Pages** → under *Build and
   deployment*, set **Source** to **GitHub Actions**. The workflow in
   `.github/workflows/deploy.yml` handles the rest.

4. Wait about a minute, then open
   `https://<your-username>.github.io/halal-market-ledger/`.

The site must be public for GitHub Pages to serve it on a free account.

---

## Layout

```
index.html               Landing page — latest run + full archive + score trends
                         (generated; do not hand-edit)
build_site.py            Regenerates index.html from data/history.json
data/history.json        Machine-readable archive: one entry per run
reports/YYYY-MM-DD.html  One self-contained report page per trading day
assets/style.css         Shared styling (light + dark themes)
.github/workflows/       Pages deployment; also rebuilds the index on push
```

`index.html` is derived. The two things that actually carry data are
`data/history.json` and the files in `reports/`.

---

## Adding a report

Each trading day, three things happen:

1. Write the day's page to `reports/YYYY-MM-DD.html`.
2. Append one object to the array in `data/history.json`.
3. Run `python3 build_site.py`, then commit and push.

The Action rebuilds the index and redeploys automatically on every push, so
step 3's rebuild is belt-and-braces — pushing steps 1 and 2 alone is enough.

### `history.json` entry shape

```jsonc
{
  "date":    "2026-08-24",              // sort key; must match the reports/ filename
  "label":   "Mon 24 Aug 2026",         // shown in the UI
  "session": "intraday 09:34-09:44 ET", // when quotes were captured
  "us_avg":  -0.83,                     // mean day move across the 35 US names
  "counts":  {"Strong Buy":3,"Buy":14,"Hold":20,"Wait":8,"Skip":3},
  "top_us":  [{"t":"MU","n":"Micron Technology, Inc.","p":906.0,"c":-6.29,"s":95.8,"u":67.2}],
  "best_ca": {"t":"STN","n":"Stantec Inc.","p":101.55,"c":-0.33,"s":73.7,"u":38.2},
  "top_etf": {"t":"SPUS","n":"SP Funds S&P 500 Sharia ETF","p":58.21,"c":-0.70},
  "note":    "One line on what drove the session.",
  "us":      [{"t":"MU","p":906.0,"c":-6.29,"s":95.8,"v":"Strong Buy"}],  // all 35
  "ca":      [{"t":"STN","p":101.55,"c":-0.33,"s":73.7,"v":"Buy"}]        // all 13
}
```

Field keys are short because they repeat 48 times per run:
`t` ticker, `n` name, `p` price, `c` day change %, `s` score, `u` upside %,
`v` verdict.

The `us` and `ca` arrays are what the score-trend sparklines are built from.
They appear once there are two or more runs.

---

## Scoring

Each of the 48 stocks is scored out of 105:

| Component        | Points |
|------------------|--------|
| Analyst upside   | 26     |
| P/E valuation    | 20     |
| Debt / equity    | 20     |
| Return on equity | 20     |
| Current ratio    | 15     |
| Day momentum     | 5      |

Bands: **80+** Strong Buy · **65–79** Buy · **48–64** Hold · **36–47** Wait ·
**under 36** Skip.

Guardrails override the score — a high total cannot buy past them:

- D/E above 3.0 → capped at Wait
- P/E above 150 → capped at Wait
- Analyst target below price → capped at Hold
- Upside under 3% → capped at Hold
- No analyst target published → capped at Hold

The weighting puts more on the balance sheet (D/E + current ratio = 35 points)
than on the analyst target (26), because forecasts are opinions and the balance
sheet is a fact.

---

## Not investment advice

An automated screen, not a recommendation to buy or sell. The scores are a fixed
formula applied to publicly reported ratios; they encode no view on business
quality, management, or anything not visible in those numbers. Shariah
compliance is a personal religious obligation — index screens disagree with one
another, and none of this substitutes for your own scholarship or a qualified
advisor.
