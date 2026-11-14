"""Assisted apply: the agent fills the form, the applicant submits it.

Two properties matter enough to pin down here.

The first is a safety interlock. The pipeline's auto-submit path is governed by
`review_only` in agent_config.json, which is a preference and can be flipped.
Assisted mode is not a preference — the applicant is sitting at the keyboard
precisely so that they review every field and sign anything that needs signing.
So `set_assisted_handoff(True)` must stop every automatic Submit click outright,
independently of what the config says.

The second is the wait itself. Submitting a form navigates to a thank-you page,
and that navigation can make a poll of the old page throw. If a transient error
ended the wait, a real submission would be misreported as skipped and the job
would sit pending forever — the exact failure this whole path exists to fix.
Only a genuinely closed window ends the wait.
"""

import datetime
import json

import assisted_apply
import web_applier


# --------------------------------------------------------------------------
# fakes
# --------------------------------------------------------------------------
class FakeBody:
    def __init__(self, page):
        self.page = page

    def inner_text(self, timeout=None):
        return self.page._next_text()


class FakePage:
    """Scripted stand-in for the live page the applicant is looking at."""

    def __init__(self, texts=None, closed=False, raise_on=()):
        self.texts = list(texts or [""])
        self.closed = closed
        self.raise_on = set(raise_on)
        self.polls = 0

    def _next_text(self):
        self.polls += 1
        if self.polls in self.raise_on:
            raise RuntimeError("navigating")
        idx = min(self.polls - 1, len(self.texts) - 1)
        return self.texts[idx]

    def is_closed(self):
        return self.closed

    def wait_for_timeout(self, _ms):
        return None

    def locator(self, _selector):
        return FakeBody(self)


# --------------------------------------------------------------------------
# the interlock
# --------------------------------------------------------------------------
def test_interlock_blocks_submit_even_when_review_only_is_off(monkeypatch):
    monkeypatch.setattr(web_applier, "is_review_only", lambda: False)
    monkeypatch.setattr(web_applier, "_submit_and_verify",
                        lambda frame, page: (_ for _ in ()).throw(
                            AssertionError("assisted mode must never click Submit")))
    monkeypatch.setattr(web_applier, "_ASSISTED_HANDOFF", True)

    result = web_applier._maybe_submit(object(), object(), answers=[])

    assert result["submitted"] is False
    assert result["attempted_submit"] is False
    assert result["declined_submit"] is True


def test_without_interlock_review_only_off_still_submits(monkeypatch):
    """The interlock narrows behaviour; it must not be the only thing holding
    the door shut, or a bug in it would silently disable normal operation."""
    monkeypatch.setattr(web_applier, "is_review_only", lambda: False)
    monkeypatch.setattr(web_applier, "_ASSISTED_HANDOFF", False)
    monkeypatch.setattr(web_applier, "_submit_and_verify", lambda frame, page: True)

    result = web_applier._maybe_submit(object(), object(), answers=[])

    assert result["submitted"] is True
    assert result["attempted_submit"] is True


def test_set_assisted_handoff_toggles_module_state():
    try:
        web_applier.set_assisted_handoff(True)
        assert web_applier._ASSISTED_HANDOFF is True
        web_applier.set_assisted_handoff(False)
        assert web_applier._ASSISTED_HANDOFF is False
    finally:
        web_applier.set_assisted_handoff(False)


# --------------------------------------------------------------------------
# the handoff wait
# --------------------------------------------------------------------------
def test_handoff_detects_submission():
    page = FakePage(texts=["Thank you for applying!"])
    assert web_applier._wait_for_human_handoff(page, timeout_s=5) == "submitted"


def test_handoff_closed_window_means_skipped():
    page = FakePage(closed=True)
    assert web_applier._wait_for_human_handoff(page, timeout_s=5) == "skipped"


def test_handoff_window_closed_midway_means_skipped():
    page = FakePage(texts=["still filling"])

    original = page.is_closed
    def closes_after_two_polls():
        return page.polls >= 2
    page.is_closed = closes_after_two_polls

    assert web_applier._wait_for_human_handoff(page, timeout_s=5) == "skipped"
    assert original() is False


def test_handoff_survives_a_transient_error_during_navigation():
    """The poll that fails is the one racing the thank-you page navigation."""
    page = FakePage(texts=["still filling", "Your application has been received"],
                    raise_on=(1,))

    assert web_applier._wait_for_human_handoff(page, timeout_s=5) == "submitted"
    assert page.polls >= 2


def test_handoff_times_out_when_nothing_happens():
    page = FakePage(texts=["still filling"])
    assert web_applier._wait_for_human_handoff(page, timeout_s=0.05) == "timeout"


# --------------------------------------------------------------------------
# the queue
# --------------------------------------------------------------------------
def _record(status="pending", category="health_informatics", days_ago=1,
            title="A Job", company="An Employer"):
    day = datetime.date.today() - datetime.timedelta(days=days_ago)
    return {
        "title": title, "company": company, "category": category,
        "url": "https://example.test/job", "status": status,
        "history": [{"status": status, "date": str(day), "note": ""}],
    }


def _queue_file(tmp_path, monkeypatch, data):
    path = tmp_path / "applications.json"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(assisted_apply, "APPLICATIONS_FILE", path)
    return path


def test_queue_is_freshest_first(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch, {
        "old": _record(days_ago=20, title="Older"),
        "new": _record(days_ago=2, title="Newer"),
        "mid": _record(days_ago=9, title="Middle"),
    })
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30)
    assert [j["title"] for j in queue] == ["Newer", "Middle", "Older"]


def test_queue_drops_stale_postings(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch, {
        "fresh": _record(days_ago=3, title="Fresh"),
        "stale": _record(days_ago=120, title="Stale"),
    })
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30)
    assert [j["title"] for j in queue] == ["Fresh"]


def test_queue_only_includes_pending(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch, {
        "a": _record(status="applied", title="Already applied"),
        "b": _record(status="not_interested", title="Rejected by him"),
        "c": _record(status="pending", title="Actually open"),
    })
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30)
    assert [j["title"] for j in queue] == ["Actually open"]


def test_queue_filters_by_category(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch, {
        "a": _record(category="health_informatics", title="Health"),
        "b": _record(category="hospitality_hotel", title="Hotel"),
    })
    queue = assisted_apply.build_queue(limit=5, category="health_informatics",
                                       max_age_days=30)
    assert [j["title"] for j in queue] == ["Health"]


def test_queue_respects_limit(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch,
                dict(("j%d" % n, _record(days_ago=n + 1, title="Job %d" % n))
                     for n in range(10)))
    assert len(assisted_apply.build_queue(limit=3, category=None, max_age_days=30)) == 3


def test_explicit_ids_bypass_every_filter(tmp_path, monkeypatch):
    """Naming a job id is a deliberate act — honour it even for a stale,
    already-closed posting the ranked queue would never surface."""
    _queue_file(tmp_path, monkeypatch, {
        "ancient": _record(status="not_interested", days_ago=400, title="Ancient"),
    })
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30,
                                       job_ids=["ancient"])
    assert [j["title"] for j in queue] == ["Ancient"]
    assert queue[0]["id"] == "ancient"


def test_unknown_id_is_skipped_not_fatal(tmp_path, monkeypatch):
    _queue_file(tmp_path, monkeypatch, {"real": _record(title="Real")})
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30,
                                       job_ids=["nope", "real"])
    assert [j["title"] for j in queue] == ["Real"]


def test_record_with_no_usable_history_is_dropped(tmp_path, monkeypatch):
    broken = _record(title="Undated")
    broken["history"] = [{"status": "pending", "note": "no date key"}]
    _queue_file(tmp_path, monkeypatch, {"broken": broken,
                                        "fine": _record(title="Dated")})
    queue = assisted_apply.build_queue(limit=5, category=None, max_age_days=30)
    assert [j["title"] for j in queue] == ["Dated"]


def test_last_seen_takes_the_most_recent_event():
    record = {"history": [
        {"status": "pending", "date": "2026-01-01"},
        {"status": "pending", "date": "2026-06-15"},
    ]}
    assert assisted_apply._last_seen(record) == datetime.date(2026, 6, 15)


def test_last_seen_handles_a_malformed_date():
    record = {"history": [{"status": "pending", "date": "not-a-date"},
                          {"status": "pending", "date": "2026-03-04"}]}
    assert assisted_apply._last_seen(record) == datetime.date(2026, 3, 4)
