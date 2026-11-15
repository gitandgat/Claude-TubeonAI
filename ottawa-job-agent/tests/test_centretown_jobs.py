"""Centretown / Remote-Canada new-jobs list — our own Peter's-New-Jobs-style digest.

The bar: a row only appears if its location is walkable from 335 Cooper St or
remote-within-Canada. A bare "Ottawa, ON" is NOT enough — the list exists to be
narrower than Peter's, so an unknown address is counted, never listed.
"""

import json

import centretown_jobs as cj


def _job(title="Health Data Analyst", company="Acme", location="", url=None, **kw):
    return {
        "id": kw.pop("id", f"id-{title}-{company}"),
        "title": title,
        "company": company,
        "location": location,
        "url": url if url is not None else f"https://example.ca/jobs/{title.replace(' ', '-')}",
        "source": kw.pop("source", "Job Bank"),
        "category": kw.pop("category", "health_informatics"),
        **kw,
    }


# ── location filter ───────────────────────────────────────────────────────────

def test_walkable_locations_are_listed_as_walk():
    for loc in ("199 Queen St, Ottawa", "Centretown, Ottawa, ON", "ByWard Market",
                "Ottawa, ON K2P 1A1", "Hybrid - Elgin St, Ottawa"):
        assert cj.section_for(_job(location=loc)) == "walk", loc


def test_remote_canada_locations_are_listed_as_remote():
    for loc in ("Remote", "Remote (Canada)", "Remote - Ontario", "Remote, Toronto, ON",
                "Work from home, Canada", "Télétravail, QC", "Remote in Canada",
                "Canada (Remote)"):
        assert cj.section_for(_job(location=loc)) == "remote", loc


def test_remote_outside_canada_is_excluded():
    for loc in ("Remote - US", "Remote, United States", "Remote - Cyprus",
                "Remote (EMEA)", "Remote - London, UK"):
        assert cj.section_for(_job(location=loc)) is None, loc


def test_generic_ottawa_and_far_locations_are_excluded():
    for loc in ("Ottawa, ON", "Ottawa", "Kanata, Ottawa", "Barrhaven", "Toronto, ON", ""):
        assert cj.section_for(_job(location=loc)) is None, loc


def test_hybrid_is_not_remote_so_needs_a_walkable_address():
    assert cj.section_for(_job(location="Hybrid remote, Ottawa, ON")) is None
    assert cj.section_for(_job(location="Hybrid, Sandy Hill")) == "walk"


def test_remote_word_in_description_does_not_make_a_job_remote():
    job = _job(location="Kanata, ON", description="Supports remote patient monitoring")
    assert cj.section_for(job) is None


def test_walkable_club_name_in_title_counts():
    """GoodLife's Workday feed puts the club name in the title/location as an intersection."""
    job = _job(title="Personal Trainer - Ottawa Queen and Bank", location="Ottawa")
    assert cj.section_for(job) == "walk"


# ── dedup key ─────────────────────────────────────────────────────────────────

def test_listing_key_ignores_tracking_params():
    a = _job(url="https://x.ca/job/1?utm_source=mc&mc_eid=abc")
    b = _job(url="https://x.ca/job/1")
    assert cj.listing_key(a) == cj.listing_key(b)


def test_listing_key_falls_back_to_id_without_url():
    assert cj.listing_key(_job(url="", id="abc123")) == "id:abc123"


# ── queue / mark-listed lifecycle ─────────────────────────────────────────────

def test_queue_adds_only_qualifying_unlisted_jobs(tmp_path):
    store = cj.Store(tmp_path)
    jobs = [
        _job("A", location="Centretown"),
        _job("B", location="Remote (Canada)"),
        _job("C", location="Ottawa, ON"),
        _job("D", location="Remote - US"),
    ]
    result = store.queue(jobs)
    assert [j["title"] for j in store.pending()] == ["A", "B"]
    assert result == {"added": 2, "unknown_ottawa": 1}


def test_queue_is_idempotent_across_runs(tmp_path):
    store = cj.Store(tmp_path)
    job = _job("A", location="Centretown")
    store.queue([job])
    store.queue([job])
    assert len(store.pending()) == 1


def test_mark_listed_clears_pending_and_blocks_requeue(tmp_path):
    store = cj.Store(tmp_path)
    job = _job("A", location="Centretown")
    store.queue([job])
    store.mark_listed(store.pending())
    assert store.pending() == []
    store.queue([job])
    assert store.pending() == [], "a job already sent must never be listed twice"


def test_store_survives_corrupt_files(tmp_path):
    (tmp_path / cj.PENDING_FILENAME).write_text("{not json")
    (tmp_path / cj.LISTED_FILENAME).write_text("[]")  # wrong shape
    store = cj.Store(tmp_path)
    assert store.pending() == []
    store.queue([_job("A", location="Centretown")])
    assert len(store.pending()) == 1


def test_pending_file_is_valid_json(tmp_path):
    store = cj.Store(tmp_path)
    store.queue([_job("A", location="Centretown")])
    data = json.loads((tmp_path / cj.PENDING_FILENAME).read_text())
    assert data[0]["section"] == "walk"


# ── rendering ─────────────────────────────────────────────────────────────────

def test_render_html_groups_and_numbers_per_section():
    items = [
        {**_job("Walk one", location="Centretown"), "section": "walk"},
        {**_job("Remote one", location="Remote"), "section": "remote"},
        {**_job("Walk two", location="Glebe"), "section": "walk"},
    ]
    html = cj.render_html(items)
    assert html.index("Walkable from Centretown") < html.index("Remote — Canada")
    assert html.count(">1.<") == 2  # numbering restarts per section, like Peter's
    assert ">2.<" in html


def test_render_html_escapes_untrusted_text():
    items = [{**_job("<script>x</script>", company="A&B", location="Centretown"),
              "section": "walk"}]
    html = cj.render_html(items)
    assert "<script>" not in html
    assert "A&amp;B" in html


def test_render_html_drops_non_http_links():
    items = [{**_job("Bad", location="Centretown", url="javascript:alert(1)"),
              "section": "walk"}]
    assert "javascript:" not in cj.render_html(items)


def test_render_empty_returns_empty_string():
    assert cj.render_html([]) == ""
    assert cj.render_text([]) == ""


def test_render_text_lists_url():
    items = [{**_job("A", location="Centretown", url="https://x.ca/1"), "section": "walk"}]
    text = cj.render_text(items)
    assert "1. A — Acme (Centretown)" in text
    assert "https://x.ca/1" in text


# ── email integration (SMTP mocked, nothing leaves the machine) ───────────────

class _FakeSMTP:
    sent = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def sendmail(self, frm, to, raw):
        _FakeSMTP.sent.append(raw)


def _decoded(raw: str) -> str:
    from email import message_from_string
    from email.header import decode_header, make_header
    msg = message_from_string(raw)
    return str(make_header(decode_header(msg["Subject"]))) + "\n" + "\n".join(
        part.get_payload(decode=True).decode("utf-8", "replace")
        for part in msg.walk() if part.get_content_maintype() == "text"
    )


def _patch_smtp(monkeypatch):
    import email_sender
    _FakeSMTP.sent = []
    monkeypatch.setattr(email_sender, "_gmail_smtp", lambda: _FakeSMTP())
    monkeypatch.setattr(email_sender, "has_sent_digest_today", lambda: False)
    monkeypatch.setattr(email_sender, "mark_digest_sent", lambda: None)
    return email_sender


def test_quiet_day_email_carries_the_list(monkeypatch):
    email_sender = _patch_smtp(monkeypatch)
    items = [{**_job("Clinic Coordinator", location="Elgin St, Ottawa"), "section": "walk"}]
    sent = email_sender.send_digest([], [], 40, jobs_list_html=cj.render_html(items),
                                    jobs_list_text=cj.render_text(items))
    assert sent
    body = _decoded(_FakeSMTP.sent[0])
    assert "new Centretown & remote jobs" in body
    assert "Clinic Coordinator" in body


def test_full_digest_carries_the_list(monkeypatch):
    email_sender = _patch_smtp(monkeypatch)
    items = [{**_job("Remote Analyst", location="Remote (Canada)"), "section": "remote"}]
    applied = [{**_job("Applied Job", location="Ottawa"), "score": 8, "status": "applied"}]
    sent = email_sender.send_digest(applied, [], 40, jobs_list_html=cj.render_html(items),
                                    jobs_list_text=cj.render_text(items))
    assert sent
    assert "Remote Analyst" in _decoded(_FakeSMTP.sent[0])


def test_placeholder_titles_and_aggregator_pages_are_dropped():
    assert cj.section_for(_job("Job Title Not Specified", location="Remote in Canada")) is None
    assert cj.section_for(_job("$13-$27/hr Remote Customer Service Rep Jobs",
                               company="ZipRecruiter", location="Remote, Canada")) is None
    assert cj.section_for(_job("Analyst", company="Not specified", location="Remote, Canada")) == "remote"
