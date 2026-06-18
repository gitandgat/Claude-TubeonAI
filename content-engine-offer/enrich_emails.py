"""
Email enrichment for the Competitor Content Engine prospect lists.

Hard rule: this NEVER invents an email. It only writes what an enrichment API
actually returns. If no API key is available, it gates cleanly and marks every
row so you know exactly what's left to do.

Key resolution (safe, in order; the key is never printed or logged):
  1. os.environ["HUNTER_API_KEY"]  (export it, or put it in your shell profile)
  2. repo keychain_secrets module, if present (guarded)
Provider: Hunter email-finder (domain + first/last name). --provider reserved
for adding Findymail later.

Usage:
    python enrich_emails.py --in scraped/tech-sales.csv --website-col website --dry-run
    python enrich_emails.py --in scraped/tech-sales.csv --website-col website --out enriched.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional

import requests  # bundles certifi -> avoids macOS Python SSL cert errors

HUNTER_FINDER = "https://api.hunter.io/v2/email-finder"

# Load repo-root .env into the environment if python-dotenv is available.
# The library reads the file at runtime; the key value is never printed here.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:  # noqa: BLE001
    pass


def resolve_key() -> Optional[str]:
    """Return the Hunter key from env/.env or repo keychain. Never logs it."""
    key = os.environ.get("HUNTER_API_KEY")
    if key:
        return key
    # Fall back to any env var whose NAME mentions HUNTER (value never printed).
    for name, val in os.environ.items():
        if "HUNTER" in name.upper() and val:
            return val
    try:  # reuse repo secret store if it exists, without assuming its API
        import keychain_secrets  # type: ignore
        for fn in ("get_secret", "get", "get_api_key"):
            f = getattr(keychain_secrets, fn, None)
            if callable(f):
                try:
                    val = f("HUNTER_API_KEY")
                    if val:
                        return val
                except Exception:  # noqa: BLE001
                    continue
    except Exception:  # noqa: BLE001
        pass
    return None


def domain_from(website: str) -> Optional[str]:
    website = (website or "").strip()
    if not website:
        return None
    if "://" not in website:
        website = "https://" + website
    host = urllib.parse.urlparse(website).netloc.lower()
    return host[4:] if host.startswith("www.") else host or None


def split_name(name: str) -> tuple[str, str]:
    # Drop parenthetical brand suffixes e.g. "Bryan Creely (A Life After Layoff)"
    cleaned = re.sub(r"\(.*?\)", "", name or "").split("&")[0]
    parts = [p.strip(".,") for p in cleaned.split() if p.strip(".,")]
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return (parts[0] if parts else ""), ""


def find_email(key: str, domain: str, first: str, last: str) -> tuple[Optional[str], Optional[int]]:
    params = {"domain": domain, "first_name": first, "last_name": last, "api_key": key}
    try:
        r = requests.get(HUNTER_FINDER, params=params, timeout=20)
        if r.status_code != 200:
            print(f"    ! {domain}: HTTP {r.status_code} {r.json().get('errors', '')}")
            return None, None
        data = r.json().get("data", {})
        return data.get("email"), data.get("score")
    except Exception as e:  # noqa: BLE001 - report, never fabricate
        print(f"    ! lookup failed for {domain}: {e}")
        return None, None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", default=None)
    p.add_argument("--name-col", default="name")
    p.add_argument("--website-col", default="website")
    p.add_argument("--provider", default="hunter", choices=["hunter"])
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    rows = list(csv.DictReader(Path(args.inp).open()))
    key = resolve_key()
    gated = key is None

    if gated:
        print("⚠ No HUNTER_API_KEY found (env or keychain). GATING — no emails fabricated.")
        print("  Fix: `export HUNTER_API_KEY=...` then re-run. Showing planned work:\n")

    out_rows = []
    for row in rows:
        name = row.get(args.name_col) or row.get("channel") or ""
        domain = domain_from(row.get(args.website_col, ""))
        first, last = split_name(name)
        email, score, status = None, None, ""

        if not domain:
            status = "needs website (check channel About/links)"
        elif gated:
            status = "ready: needs HUNTER_API_KEY"
        elif args.dry_run:
            status = f"would query hunter: {first} {last} @ {domain}"
        else:
            email, score = find_email(key, domain, first, last)
            status = "found" if email else "no match (try Findymail / manual)"

        if (gated or args.dry_run) and domain:
            print(f"  {name:<28} -> {first}.{last}@{domain}  [{status}]")

        out_rows.append({**row, "email": email or "", "email_score": score or "",
                         "enrich_status": status})

    out_path = Path(args.out) if args.out else Path(args.inp).with_name(
        Path(args.inp).stem + "-enriched.csv")
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    found = sum(1 for r in out_rows if r["email"])
    print(f"\n✓ wrote {out_path}  (emails found: {found}/{len(out_rows)}; "
          f"{'GATED — set key and re-run' if gated else 'live'})")


if __name__ == "__main__":
    main()
