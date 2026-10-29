"""Commute classification from 335 Cooper St (Centretown).

Walk is the stated priority, so the bar these tests hold is: a walkable posting
must never be classified as anything else, and an outer suburb must never be
classified as walkable — a false "walk" costs a wasted application, a false
"far" silently drops a job he'd have taken.
"""

import walkability


def test_home_address_is_cooper_street():
    """The three copies of the address (here, resume_data, autofill_sheet) are
    kept in sync by hand; this pins the one the commute logic is measured from."""
    assert walkability.HOME_ADDRESS == "335 Cooper St, Ottawa, ON"


def test_walkable_street_names():
    for text in ("199 Queen St, Ottawa", "Elgin St, Ottawa ON", "Somerset West"):
        assert walkability.classify_commute(text)["mode"] == "walk", text


def test_walkable_neighbourhoods():
    for text in ("Centretown, Ottawa, ON", "Sandy Hill", "ByWard Market", "The Glebe"):
        assert walkability.classify_commute(text)["mode"] == "walk", text


def test_goodlife_target_club_name_is_walkable():
    """GoodLife names its clubs by intersection, and that name is all the
    Workday feed's locationsText carries — "Ottawa Queen and Bank" has to
    classify on its own, without a street suffix to match."""
    assert walkability.classify_commute("Ottawa Queen and Bank")["mode"] == "walk"


def test_transit_neighbourhoods():
    for text in ("Hintonburg, Ottawa", "Westboro", "CHEO, 401 Smyth Rd", "Tunney's Pasture"):
        assert walkability.classify_commute(text)["mode"] == "transit", text


def test_far_suburbs():
    for text in ("Kanata, ON", "Orléans (ON)", "Barrhaven, Ottawa, ON", "Stittsville"):
        assert walkability.classify_commute(text)["mode"] == "far", text


def test_remote_beats_every_other_term():
    """Remote is checked first on purpose: "Remote — head office in Kanata"
    is a remote job, not a Kanata commute."""
    result = walkability.classify_commute("Remote — head office in Kanata, ON")
    assert result["mode"] == "remote"
    assert result["minutes"] == 0


def test_postal_code_detection_for_downtown_fsa():
    assert walkability.classify_commute("Office at K1P 5G4")["mode"] == "walk"


def test_postal_code_does_not_override_a_named_suburb():
    """The FSA check only runs when nothing else matched, so a Kanata postal
    code in a Kanata posting can't be read as downtown."""
    assert walkability.classify_commute("Suite 200, K2K 3G4 Kanata")["mode"] == "far"


def test_bare_ottawa_is_unknown_not_walk():
    """"Ottawa, ON" means the exact address isn't in the posting. Guessing walk
    here would hand a +1 to every Ottawa job in the pipeline."""
    result = walkability.classify_commute("Ottawa, ON")
    assert result["mode"] == "unknown"
    assert result["minutes"] is None


def test_empty_and_none_are_unknown():
    for text in ("", None):
        assert walkability.classify_commute(text)["mode"] == "unknown"


def test_every_mode_has_a_label_and_minutes_entry():
    for text in ("Queen St", "Westboro", "Kanata", "remote", "Ottawa, ON"):
        result = walkability.classify_commute(text)
        assert set(result) == {"mode", "minutes", "label"}
        assert result["label"]


def test_score_adjustment_favours_walking():
    assert walkability.commute_score_adjustment("walk") == 1
    assert walkability.commute_score_adjustment("transit") == 0
    assert walkability.commute_score_adjustment("far") == -2


def test_score_adjustment_is_neutral_when_unclear():
    """Remote and unknown must be 0, not a penalty — an unclear posting
    shouldn't be pushed under MIN_SCORE for a location it never stated."""
    assert walkability.commute_score_adjustment("remote") == 0
    assert walkability.commute_score_adjustment("unknown") == 0
    assert walkability.commute_score_adjustment("not-a-mode") == 0
