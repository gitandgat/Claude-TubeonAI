#!/usr/bin/env python3
"""Build a prefilled application package for one posting URL, without applying.

    python3 prefill_preview.py <posting-url> [--title T] [--company C] [--headed]

This is the read-only counterpart to web_applier: it opens the posting, follows
the Apply button to wherever the form actually lives, reads the questions, and
writes prefilled/<id>.html + .json — but it never types into a field and never
clicks Submit. Use it to check what the digest attachment will look like for a
given employer before letting the pipeline near it.

When the form can't be reached (Workday sign-in wall, bot check, JS-only page)
it still writes a package from the typical question set for that portal, marked
as guessed in the HTML — the same fallback the pipeline uses.
"""

import argparse
import hashlib
import sys
from urllib.parse import urlparse

import application_prefill
import form_schema
import web_applier


def _job_from_url(url: str, title: str = "", company: str = "") -> dict:
    """A minimal job dict in pipeline shape. Title and company only affect the
    package's header and the "previously employed here" answer, so a rough guess
    from the URL is fine when they aren't passed."""
    host = urlparse(url).netloc.lower()
    return {
        "id": "preview-" + hashlib.md5(url.encode()).hexdigest()[:10],
        "title": title or "Preview",
        "company": company or host.split(".")[0].replace("-", " ").title(),
        "location": "Ottawa, ON",
        "description": "",
        "url": url,
        "ats": web_applier.detect_ats(url),
    }


def _read_fields(url: str, ats: str, headed: bool):
    """Open the posting and return (fields, apply_url). Navigation and reading
    only — nothing is filled. Returns ([], url) if the form can't be reached."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        try:
            page = browser.new_page()
            page.set_default_timeout(web_applier.NAV_TIMEOUT_MS)
            page.goto(url, wait_until="domcontentloaded",
                      timeout=web_applier.NAV_TIMEOUT_MS)
            page.wait_for_timeout(2000)

            apply_button = web_applier._find_apply_button(page)
            if apply_button is not None:
                page = web_applier._follow_apply_button(page, apply_button)

            resolved_ats = web_applier._detect_ats_from_frames(page, ats)
            fields = form_schema.extract_form_fields(page, resolved_ats)
            # A bot check can park us on its own validation host. That URL is
            # single-use and worthless to a human, so hand back the posting he
            # can actually open instead.
            landed = page.url
            if web_applier._is_interstitial(landed) or not landed:
                landed = url
            return fields, landed
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="posting URL")
    parser.add_argument("--title", default="", help="job title for the package header")
    parser.add_argument("--company", default="", help="employer name")
    parser.add_argument("--headed", action="store_true",
                        help="show the browser window while it reads the form")
    args = parser.parse_args()

    job = _job_from_url(args.url, args.title, args.company)
    print("Reading {} ({})".format(args.url, job["ats"]))

    try:
        fields, apply_url = _read_fields(args.url, job["ats"], args.headed)
    except Exception as e:
        print("  could not reach the form: {}".format(e))
        fields, apply_url = [], args.url

    if fields:
        print("  found {} questions on the form".format(len(fields)))
    else:
        print("  no form reached — falling back to the typical question set")

    result = application_prefill.build_prefill(
        job, fields, cover_letter="", resume_pdf="", apply_url=apply_url)

    print("\n{} ready, {} need his input ({} of them required)".format(
        result["n_ready"], result["n_needs_input"], result["n_required_needs_input"]))
    for answer in result["answers"]:
        mark = "!" if answer["needs_input"] else "."
        value = answer["hint"] if answer["needs_input"] else answer["answer"]
        print("  {} {}: {}".format(mark, answer["label"][:60], str(value)[:70]))

    print("\nApply here: {}".format(result["apply_url"]))
    print("Package:    {}".format(result["html"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
