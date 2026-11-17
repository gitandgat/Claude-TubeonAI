"""Tests du moteur de la semaine (le-cahier/engine/semaine.py).

Aucun appel réseau : la génération et la voix ne sont pas testées ici, seulement
ce qui décide si une phrase entre dans le cahier, où tombe chaque son dans la
piste, et la tenue des fichiers entre fabrication et publication.

    python3 -m pytest le-cahier/engine/test_semaine.py -q
"""

import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semaine  # noqa: E402

PROF = {"level": 2, "domains": ["sante"], "why": "", "l1": ""}
GOOD = {
    "s": "Le patient se plaint d'une douleur ___ depuis trois jours.",
    "a": "persistante",
    "d": ["bruyante", "gratuite", "salée"],
    "g": "The patient has had a persistent pain for three days.",
    "lv": 2,
}


# ------------------------------------------------------------ clés de la carte


@pytest.mark.unit
@pytest.mark.parametrize(
    "phrase, key",
    [
        (
            "Dépêche-toi, le train part dans deux minutes.",
            "depechetoiletrainpartdansdeuxminutes",
        ),
        (
            "Cette recette demande trois œufs et du beurre.",
            "cetterecettedemandetroisufsetdubeurre",
        ),
        (
            "À peine était-il entré que le téléphone a sonné.",
            "apeineetaitilentrequeletelephoneasonne",
        ),
    ],
)
def test_d_strip_matches_the_javascript_keys(phrase, key):
    assert semaine.d_strip(phrase) == key


@pytest.mark.unit
def test_every_legacy_recording_key_comes_from_a_base_sentence():
    assert semaine.selftest() == 0


# ------------------------------------------------------------ validation


@pytest.mark.unit
def test_validate_accepts_a_well_formed_sentence():
    e, why = semaine.validate(GOOD, PROF, set())
    assert why is None
    assert e == {**GOOD}


@pytest.mark.unit
@pytest.mark.parametrize(
    "patch, reason",
    [
        ({"s": "Le ___ se plaint d'une douleur ___ depuis trois jours."}, "trou"),
        ({"s": "Il a pris ___ comprimés depuis 3 jours, sans effet."}, "chiffres"),
        (
            {"s": "Une douleur persistante, une douleur ___ depuis longtemps."},
            "réponse visible",
        ),
        ({"d": ["bruyante", "Bruyante", "salée"]}, "distracteurs"),
        ({"d": ["bruyante", "persistante", "salée"]}, "distracteurs"),
        ({"s": "Douleur ___ ici."}, "mots"),
        ({"g": ""}, "trou ou champ"),
        ({"d": "bruyante"}, "champ manquant"),
    ],
)
def test_validate_rejects_what_would_break_a_card(patch, reason):
    e, why = semaine.validate({**GOOD, **patch}, PROF, set())
    assert e is None
    assert reason in why


@pytest.mark.unit
def test_validate_rejects_a_sentence_already_in_the_notebook():
    seen = {semaine.d_strip(GOOD["s"].replace("___", GOOD["a"]))}
    e, why = semaine.validate(GOOD, PROF, seen)
    assert e is None and why == "déjà connue"


@pytest.mark.unit
@pytest.mark.parametrize("lv, expected", [(5, 2), (0, 2), ("B1", 2), (1, 1)])
def test_validate_keeps_the_level_within_reach(lv, expected):
    e, _ = semaine.validate({**GOOD, "lv": lv}, PROF, set())
    assert e["lv"] == expected


@pytest.mark.unit
def test_extract_json_array_ignores_markdown_fences():
    text = 'Voici :\n```json\n[{"s":"a"}]\n```\n'
    assert semaine.extract_json_array(text) == [{"s": "a"}]


@pytest.mark.unit
def test_extract_json_array_refuses_text_without_an_array():
    with pytest.raises(ValueError):
        semaine.extract_json_array("pas de JSON ici")


# ------------------------------------------------------------ semaines


@pytest.mark.unit
@pytest.mark.parametrize(
    "day, expected",
    [
        (dt.date(2026, 11, 15), ("2026-W46", "26w46")),
        (dt.date(2026, 11, 16), ("2026-W47", "26w47")),
        (dt.date(2027, 1, 1), ("2026-W53", "26w53")),
    ],
)
def test_week_of_uses_iso_weeks(day, expected):
    assert semaine.week_of(day) == expected


# ------------------------------------------------------------ fichiers du cahier


@pytest.mark.unit
def test_phrases_and_voice_map_survive_a_round_trip(tmp_path):
    items = [{"id": "n264600", **GOOD, "w": "2026-W46"}]
    rec = {"abc": [0.0, 2.1], "def": [0.0, 1.5, "voix-26w46.mp3"]}
    semaine.write_phrases(tmp_path / "phrases.js", items)
    semaine.write_voix(tmp_path / "voix-map.js", rec)
    assert semaine.read_js_json(tmp_path / "phrases.js", "TROU_PLUS") == items
    assert semaine.read_js_json(tmp_path / "voix-map.js", "VOIX_REC") == rec


@pytest.mark.unit
def test_an_empty_week_file_is_still_valid(tmp_path):
    semaine.write_phrases(tmp_path / "phrases.js", [])
    assert semaine.read_js_json(tmp_path / "phrases.js", "TROU_PLUS") == []


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg absent")
def test_build_shard_places_each_sentence_where_the_map_says(tmp_path):
    clips = []
    for i, sec in enumerate((1.0, 0.6)):
        p = tmp_path / f"t{i}.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency=440:duration={sec}",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(p),
            ],
            check=True,
        )
        clips.append(p)
    entries = semaine.build_shard(clips, tmp_path / "v.mp3", "v.mp3")
    pre, post = semaine.PRE, semaine.POST
    assert entries[0] == [0.0, round(pre + 1.0, 2), "v.mp3"]
    assert entries[1][0] == pytest.approx(pre + 1.0 + post, abs=0.01)
    assert entries[1][1] == pytest.approx(pre + 0.6, abs=0.01)
    assert semaine.duration(tmp_path / "v.mp3") == pytest.approx(
        2 * (pre + post) + 1.6, abs=0.1
    )


# ------------------------------------------------------------ fabrication → publication


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    cahier = tmp_path / "le-cahier"
    out = cahier / "engine" / "out"
    out.mkdir(parents=True)
    monkeypatch.setattr(semaine, "CAHIER", cahier)
    monkeypatch.setattr(semaine, "OUT", out)
    monkeypatch.setattr(semaine, "STATE", cahier / "engine" / "state.json")
    monkeypatch.setattr(semaine, "PROFILE", cahier / "engine" / "profil.json")
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    return cahier, out


def _fake_batch(out, week, shard):
    d = out / week
    (d / "clips").mkdir(parents=True)
    (d / "phrases.js").write_text("const TROU_PLUS = [];\n", encoding="utf-8")
    (d / "voix-map.js").write_text("const VOIX_REC = {};\n", encoding="utf-8")
    (d / shard).write_bytes(b"ID3")
    (d / "index.html").write_text("<title>Le Cahier</title>", encoding="utf-8")
    (d / "manifest.json").write_text(
        json.dumps(
            {"week": week, "shard": shard, "ids": ["n264600"], "published": False}
        ),
        encoding="utf-8",
    )
    return d


@pytest.mark.unit
def test_pending_finds_the_oldest_unpublished_week(sandbox):
    _, out = sandbox
    assert semaine.pending() is None
    _fake_batch(out, "2026-W47", "voix-26w47.mp3")
    _fake_batch(out, "2026-W46", "voix-26w46.mp3")
    assert semaine.pending().name == "2026-W46"


@pytest.mark.unit
def test_dry_runs_never_count_as_pending(sandbox):
    _, out = sandbox
    _fake_batch(out, "dry-2026-W46", "voix-26w46.mp3")
    assert semaine.pending() is None


@pytest.mark.unit
def test_mark_published_updates_the_mirror_and_the_record(sandbox):
    cahier, out = sandbox
    d = _fake_batch(out, "2026-W46", "voix-26w46.mp3")
    semaine.mark_published("2026-W46", "47")
    for f in ("phrases.js", "voix-map.js", "voix-26w46.mp3", "index.html"):
        assert (cahier / f).exists(), f
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert m["published"] and m["version"] == "47"
    assert semaine.load_state()["weeks"]["2026-W46"]["version"] == "47"
    assert not (d / "clips").exists()
    assert semaine.pending() is None


@pytest.mark.unit
def test_profile_from_takes_what_the_learner_set_and_keeps_the_rest(sandbox, tmp_path):
    (semaine.PROFILE).write_text(
        json.dumps(
            {
                "level": 2,
                "domains": ["sante", "travail"],
                "why": "Travailler à Ottawa",
                "l1": "anglais",
            }
        ),
        encoding="utf-8",
    )
    prog = tmp_path / "progress.json"
    prog.write_text(
        json.dumps({"level": 3, "profil": {"domains": [], "why": "", "l1": ""}}),
        encoding="utf-8",
    )
    semaine.profile_from(prog)
    p = semaine.load_profile()
    assert p["level"] == 3
    assert p["domains"] == ["sante", "travail"]
    assert p["why"] == "Travailler à Ottawa"
    prog.write_text(
        json.dumps({"level": 3, "profil": {"domains": ["sport", "bogus"]}}),
        encoding="utf-8",
    )
    semaine.profile_from(prog)
    assert semaine.load_profile()["domains"] == ["sport"]


# ------------------------------------------------------------ orchestration, sans réseau


GOOD2 = {
    **GOOD,
    "s": "Je dois ___ mon rendez-vous chez le dentiste demain matin.",
    "a": "déplacer",
    "d": ["traduire", "cuisiner", "vendre"],
    "g": "I need to move my dentist appointment tomorrow morning.",
}
GOOD3 = {
    **GOOD,
    "s": "La pharmacienne m'a ___ de prendre ce sirop après les repas.",
    "a": "conseillé",
    "d": ["interdit", "promis", "volé"],
    "g": "The pharmacist advised me to take this syrup after meals.",
}


@pytest.mark.unit
def test_generate_asks_again_until_it_has_enough_good_sentences(monkeypatch):
    replies = [[GOOD, {**GOOD, "d": "x"}, GOOD], [GOOD2, GOOD3]]
    calls = []

    def fake_ask(prompt):
        calls.append(prompt)
        return replies[len(calls) - 1], "fake-model"

    monkeypatch.setattr(semaine, "ask_claude", fake_ask)
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    kept, model = semaine.generate(3, PROF, set(), [])
    assert [k["a"] for k in kept] == ["persistante", "déplacer", "conseillé"]
    assert len(calls) == 2 and model == "fake-model"
    assert (
        "Le patient se plaint d'une douleur persistante" in calls[1]
    )  # the retry knows what's done


@pytest.mark.integration
@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg absent")
def test_a_full_week_runs_offline_and_never_pays_twice(sandbox, monkeypatch):
    cahier, out = sandbox
    (cahier / "cahier.js").write_text(
        'const TROU = [\n  {id:"t1", s:"Il pleut, prends ton ___.", a:"parapluie", d:["a","b","c"], g:"x"}\n];\n',
        encoding="utf-8",
    )
    semaine.write_phrases(cahier / "phrases.js", [])
    semaine.write_voix(
        cahier / "voix-map.js", {"ilpleutprendstonparapluie": [0.0, 1.5]}
    )
    asked = []

    def fake_ask(prompt):
        asked.append(prompt)
        return [GOOD, GOOD2, GOOD3], "fake-model"

    def fake_tts(text, out_wav):
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=330:duration=0.8",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(out_wav),
            ],
            check=True,
        )
        return True

    monkeypatch.setattr(semaine, "ask_claude", fake_ask)
    monkeypatch.setattr(semaine, "tts", fake_tts)
    week, code = semaine.week_of()

    assert semaine.run(3, dry=False, force=False) == 0
    d = out / week
    plus = semaine.read_js_json(d / "phrases.js", "TROU_PLUS")
    rec = semaine.read_js_json(d / "voix-map.js", "VOIX_REC")
    assert [p["id"] for p in plus] == [
        f"n{code.replace('w', '')}0{i}" for i in range(3)
    ]
    assert all(p["w"] == week for p in plus)
    assert rec["ilpleutprendstonparapluie"] == [0.0, 1.5]  # the old map is kept
    new = [rec[semaine.d_strip(p["s"].replace("___", p["a"]))] for p in plus]
    assert [seg[2] for seg in new] == [f"voix-{code}.mp3"] * 3
    assert new[1][0] == pytest.approx(semaine.PRE + 0.8 + semaine.POST, abs=0.01)
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert m["base"]["phrases.js"] == semaine.sha256(cahier / "phrases.js")
    assert semaine.pending() == d

    assert semaine.run(3, dry=False, force=False) == 0  # already built: no new spend
    assert len(asked) == 1


# ------------------------------------------------------------ les deux appels réseau, simulés


class _Resp:
    def __init__(self, ok=True, status=200, payload=None, content=b""):
        self.ok, self.status_code, self._p, self.content = ok, status, payload, content

    def json(self):
        return self._p


@pytest.mark.unit
def test_tts_keeps_only_a_real_wav_and_retries_otherwise(monkeypatch, tmp_path):
    posts = iter(
        [
            _Resp(payload={"code": 1, "message": "busy"}),  # refused
            _Resp(
                payload={"code": 0, "data": {"details": {"url": "https://x/a.wav"}}}
            ),  # url → not a WAV
            _Resp(
                payload={"code": 0, "data": {"details": {"url": "https://x/b.wav"}}}
            ),  # url → WAV
        ]
    )
    gets = iter(
        [_Resp(content=b"<html>expired</html>"), _Resp(content=b"RIFF....WAVEfmt ")]
    )
    monkeypatch.setenv("VOISPARK_API_KEY", "test-key")
    monkeypatch.setattr(semaine.requests, "post", lambda *a, **k: next(posts))
    monkeypatch.setattr(semaine.requests, "get", lambda *a, **k: next(gets))
    monkeypatch.setattr(semaine.time, "sleep", lambda s: None)
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    assert semaine.tts("Bonjour.", tmp_path / "c.wav") is True
    assert (tmp_path / "c.wav").read_bytes().startswith(b"RIFF")


@pytest.mark.unit
def test_tts_gives_up_after_three_failures(monkeypatch, tmp_path):
    monkeypatch.setenv("VOISPARK_API_KEY", "test-key")
    monkeypatch.setattr(
        semaine.requests,
        "post",
        lambda *a, **k: _Resp(ok=False, status=503, payload={}),
    )
    monkeypatch.setattr(semaine.time, "sleep", lambda s: None)
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    assert semaine.tts("Bonjour.", tmp_path / "c.wav") is False
    assert not (tmp_path / "c.wav").exists()


@pytest.fixture
def fake_anthropic(monkeypatch):
    """Un module « anthropic » de poche : le premier modèle n'existe pas, le second répond."""
    import types

    mod = types.ModuleType("anthropic")

    class _Err(Exception):
        pass

    mod.NotFoundError = type("NotFoundError", (_Err,), {})
    mod.PermissionDeniedError = type("PermissionDeniedError", (_Err,), {})
    mod.BadRequestError = type("BadRequestError", (_Err,), {})
    tried = []

    class _Messages:
        def create(self, model, max_tokens, messages):
            tried.append(model)
            if model == "missing-model":
                raise mod.NotFoundError("model not found")
            if (
                model == "sloppy-model" and len(messages) == 1
            ):  # first answer: broken JSON
                bad = types.SimpleNamespace(text='[{"s":"Il a dit "bonjour" ici"}]')
                return types.SimpleNamespace(content=[bad])
            if model == "hopeless-model":  # never manages valid JSON, even when asked
                return types.SimpleNamespace(
                    content=[types.SimpleNamespace(text="[{oops")]
                )
            block = types.SimpleNamespace(text='```json\n[{"s":"ok"}]\n```')
            return types.SimpleNamespace(content=[block])

    mod.Anthropic = lambda: types.SimpleNamespace(messages=_Messages())
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    return tried


@pytest.mark.unit
def test_ask_claude_falls_back_to_the_next_model(fake_anthropic, monkeypatch):
    monkeypatch.setattr(semaine, "MODELS", ["missing-model", "good-model"])
    items, model = semaine.ask_claude("prompt")
    assert items == [{"s": "ok"}] and model == "good-model"
    assert fake_anthropic == ["missing-model", "good-model"]


@pytest.mark.unit
def test_ask_claude_reports_when_no_model_is_usable(fake_anthropic, monkeypatch):
    monkeypatch.setattr(semaine, "MODELS", ["missing-model"])
    with pytest.raises(RuntimeError, match="aucun modèle"):
        semaine.ask_claude("prompt")


@pytest.mark.unit
def test_pending_flag_gives_the_wrapper_a_clean_exit_code(sandbox, monkeypatch, capsys):
    _, out = sandbox
    monkeypatch.setattr(sys, "argv", ["semaine.py", "--pending", "--print"])
    assert semaine.main() == 1
    _fake_batch(out, "2026-W46", "voix-26w46.mp3")
    assert semaine.main() == 0
    assert capsys.readouterr().out.strip().endswith("2026-W46")


@pytest.mark.unit
def test_ask_claude_repairs_broken_json_once(fake_anthropic, monkeypatch):
    monkeypatch.setattr(semaine, "MODELS", ["sloppy-model"])
    items, model = semaine.ask_claude("prompt")
    assert items == [{"s": "ok"}] and model == "sloppy-model"
    assert fake_anthropic == [
        "sloppy-model",
        "sloppy-model",
    ]  # answer + one repair, no more


@pytest.mark.unit
def test_ask_claude_gives_up_cleanly_when_the_repair_fails_too(
    fake_anthropic, monkeypatch
):
    monkeypatch.setattr(semaine, "MODELS", ["hopeless-model"])
    with pytest.raises(ValueError):
        semaine.ask_claude("prompt")


@pytest.mark.unit
def test_generate_survives_an_unreadable_answer(monkeypatch):
    replies = iter([ValueError("not JSON"), [GOOD, GOOD2]])

    def fake_ask(prompt):
        r = next(replies)
        if isinstance(r, Exception):
            raise r
        return r, "fake-model"

    monkeypatch.setattr(semaine, "ask_claude", fake_ask)
    monkeypatch.setattr(semaine, "log", lambda msg: None)
    kept, _ = semaine.generate(2, PROF, set(), [])
    assert [k["a"] for k in kept] == ["persistante", "déplacer"]


@pytest.mark.unit
def test_profile_set_accepts_only_a_level_and_known_domains(sandbox):
    semaine.PROFILE.write_text(
        json.dumps({"level": 2, "domains": ["sante"], "why": "Travailler à Ottawa"}),
        encoding="utf-8",
    )
    semaine.profile_set(4, "travail, sport ,bogus;rm -rf")
    p = semaine.load_profile()
    assert p["level"] == 4
    assert p["domains"] == ["travail", "sport"]
    assert p["why"] == "Travailler à Ottawa"
    semaine.profile_set(None, "")  # nothing usable: nothing changes
    assert semaine.load_profile()["domains"] == ["travail", "sport"]
    semaine.profile_set(9, None)  # out of range: level kept
    assert semaine.load_profile()["level"] == 4
