# -*- coding: utf-8 -*-
"""
Investor chatter — recent cashtag mentions from a short list of watched X/Twitter
accounts, cross-checked against the Halal Market Ledger universe.

Requires the X API v2 (a paid developer plan — the free tier cannot search or
read timelines). Set X_BEARER_TOKEN as a GitHub Actions secret / env var.

This is commentary, not a signal: these accounts rarely tweet an explicit "I
bought X", and a mention here is not confirmation of any trade. If the token
is missing or the API errors, this module returns an empty result rather than
failing the run — investor chatter is decoration on the report, never a
reason to abort a daily publish.
"""
import os

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

API = "https://api.twitter.com/2"

# handle -> (display name, firm)
WATCHED = [
    ("BillAckman", "Bill Ackman", "Pershing Square"),
    ("michaeljburry", "Michael Burry", "Scion Asset Management"),
    ("chamath", "Chamath Palihapitiya", "Social Capital"),
]


class TweetsUnavailable(Exception):
    pass


def _headers(token):
    return {"Authorization": "Bearer %s" % token}


def _user_id(handle, token):
    r = requests.get("%s/users/by/username/%s" % (API, handle),
                      headers=_headers(token), timeout=10)
    r.raise_for_status()
    return r.json()["data"]["id"]


def _recent_tweets(user_id, token, max_results=10):
    r = requests.get(
        "%s/users/%s/tweets" % (API, user_id),
        headers=_headers(token),
        params={
            "max_results": max_results,
            "exclude": "retweets,replies",
            "tweet.fields": "created_at,entities,public_metrics",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("data") or []


def fetch(tickers, token=None, log=None):
    """Return tweets from WATCHED accounts that cashtag a ticker in `tickers`.

    tickers: iterable of bare symbols (no exchange suffix, no $) considered
             "in universe" — a mention of anything else is dropped.
    Returns [] on any missing token, missing `requests`, or API failure.
    """
    log = log or (lambda msg: None)
    token = token or os.environ.get("X_BEARER_TOKEN")
    if not token:
        log("investor tweets: X_BEARER_TOKEN not set — skipping")
        return []
    if requests is None:
        log("investor tweets: 'requests' not installed — skipping")
        return []

    universe = {t.upper() for t in tickers}
    hits = []
    for handle, name, firm in WATCHED:
        try:
            uid = _user_id(handle, token)
            for tw in _recent_tweets(uid, token):
                cashtags = [c["tag"].upper()
                            for c in (tw.get("entities", {}) or {}).get("cashtags", [])]
                matched = [t for t in cashtags if t in universe]
                if not matched:
                    continue
                hits.append({
                    "handle": handle, "name": name, "firm": firm,
                    "text": tw["text"], "created_at": tw.get("created_at"),
                    "tickers": matched,
                    "url": "https://x.com/%s/status/%s" % (handle, tw["id"]),
                })
        except Exception as ex:  # noqa: BLE001 — one account failing shouldn't drop the rest
            log("investor tweets: %s failed: %s" % (handle, str(ex)[:120]))
            continue
    hits.sort(key=lambda h: h.get("created_at") or "", reverse=True)
    return hits
