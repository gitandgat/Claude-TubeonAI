"""Food-photo nutrition analysis: Claude vision identifies foods, USDA FDC supplies the numbers.

Mirrors Longevity-Nutrition's analyze-meal edge function (same nutrient IDs, same FDC
query shape, same per-100g scaling) so this surface and the web app agree.

    python3 nutrition.py <photo> [--note "half the rice"]
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
load_dotenv(BASE.parent / ".env")

VISION_MODEL = "claude-sonnet-5"
FDC_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
FDC_TIMEOUT = 25

# USDA FoodData Central nutrient IDs.
NUTRIENT_IDS = {
    "calories": 1008,
    "protein": 1003,
    "carbs": 1005,
    "fat": 1004,
    "fiber": 1079,
    "vitamin_d": 1114,
    "magnesium": 1090,
    "potassium": 1092,
    "iron": 1089,
    "zinc": 1095,
    "calcium": 1087,
    "vitamin_c": 1162,
    "b12": 1178,
    "epa": 1278,
    "dha": 1272,
}

WEIGHT_KG = 85
HEIGHT_CM = 179
AGE = 31

# The app's "athlete" tier. It assumes hard daily training on top of general activity;
# if bodyweight climbs faster than ~0.5 kg/week, 1.725 ("very active") is the truer
# figure. The scale over two to three weeks settles it, not the formula.
ACTIVITY_MULTIPLIER = 1.9
MUSCLE_GAIN_SURPLUS = 300
PROTEIN_G_PER_LB = 1.0  # midpoint of the 0.9-1.1 muscle-gain range, i.e. 2.2 g/kg


def _daily_targets() -> dict[str, float]:
    """Mifflin-St Jeor, matching Longevity-Nutrition's calculateDailyTargets.

    Derived rather than hardcoded so this agrees with the web app, which recomputes
    from the same profile. Change a constant above and both macros and the split follow.
    """
    bmr = 10 * WEIGHT_KG + 6.25 * HEIGHT_CM - 5 * AGE + 5  # male
    calories = round(bmr * ACTIVITY_MULTIPLIER + MUSCLE_GAIN_SURPLUS)
    protein_g = round(WEIGHT_KG * 2.205 * PROTEIN_G_PER_LB)
    fat_g = round(calories * 0.3 / 9)
    carbs_g = round((calories - protein_g * 4 - fat_g * 9) / 4)
    return {
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fiber_g": 35,
    }


MACRO_TARGETS = _daily_targets()

# US RDA, adult male. Used only to show "% of day" context, not as medical advice.
MICRO_TARGETS = {
    "vitamin_d_iu": (600, "IU", "Vitamin D"),
    "omega_3_g": (1.6, "g", "Omega-3"),
    "magnesium_mg": (420, "mg", "Magnesium"),
    "potassium_mg": (3400, "mg", "Potassium"),
    "iron_mg": (8, "mg", "Iron"),
    "zinc_mg": (11, "mg", "Zinc"),
    "calcium_mg": (1000, "mg", "Calcium"),
    "vitamin_c_mg": (90, "mg", "Vitamin C"),
    "vitamin_b12_mcg": (2.4, "mcg", "Vitamin B12"),
}

EXTRACT_FOODS_TOOL = {
    "name": "extract_foods",
    "description": "Extract the identified foods in this meal",
    "input_schema": {
        "type": "object",
        "properties": {
            "foods": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Display name of the food"},
                        "fdc_query": {
                            "type": "string",
                            "description": "Clean search term for USDA FoodData Central (e.g. 'grilled chicken breast')",
                        },
                        "portion_grams": {"type": "number", "description": "Estimated portion size in grams"},
                        "confidence": {"type": "number", "description": "Confidence 0-1 the food is correctly identified"},
                    },
                    "required": ["name", "fdc_query", "portion_grams", "confidence"],
                },
            }
        },
        "required": ["foods"],
    },
}


@dataclass
class Food:
    name: str
    fdc_query: str
    portion_grams: float
    confidence: float
    nutrients: dict[str, float] = field(default_factory=dict)
    fdc_match: str | None = None


@dataclass
class MealReport:
    foods: list[Food]
    totals: dict[str, float]
    unmatched: list[str]


class NoFoodFound(Exception):
    """The message or photo did not describe food — not a failure, just not a meal."""


def _client() -> Anthropic:
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _image_block(photo: Path) -> dict:
    media_type = mimetypes.guess_type(photo.name)[0] or "image/jpeg"
    if media_type not in {"image/jpeg", "image/png", "image/gif", "image/webp"}:
        raise ValueError(f"Unsupported image type {media_type!r} — use jpeg, png, gif, or webp.")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.b64encode(photo.read_bytes()).decode(),
        },
    }


# Drinks are described by volume, but FDC is per 100g, so the model converts.
PORTION_GUIDANCE = (
    "Give a clean USDA FoodData Central search term for each — generic and specific, like "
    "'grilled chicken breast' or 'brown rice, cooked'.\n"
    "Portions must be in grams. For drinks, convert volume to grams: water and coffee are "
    "1.0 g/ml, juice and milk about 1.03 g/ml, a protein shake made with water about 1.02 g/ml. "
    "One scoop of protein powder is about 30g unless stated otherwise. Count a drink's "
    "ingredients separately when they are given separately (whey powder and the milk it is "
    "mixed into are two entries), and as one entry when it is a bought product."
)


def identify_foods(photo: Path | None = None, text: str | None = None) -> list[Food]:
    """Identify foods from a photo, a written description, or a photo plus caption."""
    if photo is None and not text:
        raise ValueError("Need a photo or a description of the meal.")

    content: list[dict] = []
    if photo is not None:
        content.append(_image_block(photo))
        prompt = (
            "Identify every distinct food and drink in this meal photo. Estimate each portion in "
            "grams using visible references (plate size, utensils, hand).\n" + PORTION_GUIDANCE
        )
        if text:
            prompt += f"\n\nThe person adds: {text}"
    else:
        prompt = (
            "Identify every distinct food and drink in this meal description. Use the stated "
            "amounts; where an amount is missing, assume one ordinary serving and say so in the "
            "name.\n"
            "If the message does not describe food or drink at all — a greeting, a question, "
            "anything else — return an empty foods list. Never invent a placeholder food.\n"
            + PORTION_GUIDANCE
            + f"\n\nThe message: {text}"
        )

    content.append({"type": "text", "text": prompt})

    result = _client().messages.create(
        model=VISION_MODEL,
        max_tokens=1024,
        tools=[EXTRACT_FOODS_TOOL],
        tool_choice={"type": "tool", "name": "extract_foods"},
        messages=[{"role": "user", "content": content}],
    )

    for block in result.content:
        if block.type == "tool_use":
            return _parse_foods(block.input.get("foods"))
    raise RuntimeError("Claude returned no food identification for this meal.")


def _parse_foods(raw: object) -> list[Food]:
    """Normalise the tool's `foods` value.

    Tool output is model output: the schema is a strong hint, not a guarantee. It has
    come back with `foods` as a JSON string, whose characters then unpacked into
    Food(**"a"). Anything unreadable is skipped rather than allowed to abort the meal.
    """
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError("Could not read the food list the model returned.") from None
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise RuntimeError("Could not read the food list the model returned.")

    foods: list[Food] = []
    for item in raw:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                continue
        if not isinstance(item, dict):
            continue

        name = item.get("name") or item.get("fdc_query")
        query = item.get("fdc_query") or item.get("name")
        if not name or not query:
            continue
        try:
            grams = float(item.get("portion_grams"))
            confidence = float(item.get("confidence", 0.5))
        except (TypeError, ValueError):
            continue
        if grams <= 0:
            continue

        foods.append(
            Food(name=str(name), fdc_query=str(query), portion_grams=grams, confidence=confidence)
        )

    if not foods:
        raise NoFoodFound
    return foods


def _clean_query(query: str) -> str:
    """FDC answers 400 to parentheses and other punctuation, so send bare words."""
    cleaned = "".join(c if c.isalnum() or c.isspace() or c == "-" else " " for c in query)
    return " ".join(cleaned.split())


def _energy_per_100g(food: dict) -> float | None:
    for n in food.get("foodNutrients", []):
        if n.get("nutrientId") == NUTRIENT_IDS["calories"] and n.get("value") is not None:
            return n["value"]
    return None


def fetch_fdc_candidates(query: str, api_key: str) -> list[dict]:
    """USDA entries that could be this food, best-ranked first.

    Rows without an energy value are dropped: FDC search omits nutrients on some
    entries ("Mushrooms, white button"), and scaling an absent value yields a
    confident-looking 0 kcal.
    """
    # Key goes in a header, never the query string — a URL ends up in tracebacks and logs.
    res = requests.get(
        FDC_SEARCH_URL,
        params={"query": _clean_query(query), "pageSize": 10, "dataType": "Foundation,SR Legacy"},
        headers={"X-Api-Key": api_key},
        timeout=FDC_TIMEOUT,
    )
    res.raise_for_status()
    return [f for f in (res.json().get("foods") or []) if _energy_per_100g(f) is not None]


def nutrients_for(food: dict, portion_grams: float) -> dict[str, float]:
    """Scale a USDA entry's per-100g nutrients to this portion."""
    by_id = {n["nutrientId"]: n["value"] for n in food.get("foodNutrients", []) if n.get("value") is not None}
    scale = portion_grams / 100

    def get(key: str) -> float | None:
        value = by_id.get(NUTRIENT_IDS[key])
        return round(value * scale, 2) if value is not None else None

    nutrients: dict[str, float] = {
        "calories": get("calories") or 0,
        "protein_g": get("protein") or 0,
        "carbs_g": get("carbs") or 0,
        "fat_g": get("fat") or 0,
        "fiber_g": get("fiber") or 0,
    }

    omega3 = (get("epa") or 0) + (get("dha") or 0)
    if omega3 > 0:
        nutrients["omega_3_g"] = round(omega3 / 1000, 2)

    for key, label in (
        ("vitamin_d", "vitamin_d_iu"),
        ("magnesium", "magnesium_mg"),
        ("potassium", "potassium_mg"),
        ("iron", "iron_mg"),
        ("zinc", "zinc_mg"),
        ("calcium", "calcium_mg"),
        ("vitamin_c", "vitamin_c_mg"),
        ("b12", "vitamin_b12_mcg"),
    ):
        value = get(key)
        if value is not None:
            nutrients[label] = value

    return nutrients


def select_matches(foods: list[Food], candidates: list[list[dict]]) -> list[int | None]:
    """Choose which USDA entry represents each food, or None when none does.

    USDA's relevance ranking cannot be trusted positionally — "grilled carrot" ranks
    grilled kielbasa first, and "mixed salad greens" returns only dressings and oils,
    where any pick would be wrong. Judging the shortlist needs food knowledge, so
    Claude does it in one call for the whole meal.
    """
    listing = []
    for i, (food, options) in enumerate(zip(foods, candidates)):
        lines = [f"Food {i}: {food.name} (eaten: {food.fdc_query})"]
        lines += [
            f"   {j}. {c.get('description')} — {_energy_per_100g(c):.0f} kcal/100g"
            for j, c in enumerate(options)
        ]
        if not options:
            lines.append("   (no candidates)")
        listing.append("\n".join(lines))

    tool = {
        "name": "select_matches",
        "description": "Choose the USDA entry for each food",
        "input_schema": {
            "type": "object",
            "properties": {
                "choices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "food_index": {"type": "integer"},
                            "candidate_index": {
                                "type": ["integer", "null"],
                                "description": "Index of the best USDA entry, or null if none represents this food",
                            },
                        },
                        "required": ["food_index", "candidate_index"],
                    },
                }
            },
            "required": ["choices"],
        },
    }

    prompt = (
        "For each food below, pick the USDA entry that best represents it as eaten.\n\n"
        "Rules:\n"
        "- It must be the same food. A dressing is not salad greens; a pasta entree is not "
        "a tomato slice; grilled kielbasa is not a grilled carrot.\n"
        "- A different cooking method is fine and much better than no match: pick "
        "'Broccoli, raw' for steamed broccoli if that is the closest entry. Prefer a cooked "
        "entry when one exists.\n"
        "- Never pick a dried, dehydrated, powdered, instant or oil entry for a fresh or "
        "cooked food — those are several times more calorie-dense.\n"
        "- Answer null only when no entry is the same food at all.\n\n"
        + "\n\n".join(listing)
    )

    result = _client().messages.create(
        model=VISION_MODEL,
        max_tokens=1024,
        tools=[tool],
        tool_choice={"type": "tool", "name": "select_matches"},
        messages=[{"role": "user", "content": prompt}],
    )

    chosen: list[int | None] = [None] * len(foods)
    for block in result.content:
        if block.type == "tool_use":
            for choice in block.input["choices"]:
                i, j = choice["food_index"], choice["candidate_index"]
                if 0 <= i < len(foods) and j is not None and 0 <= j < len(candidates[i]):
                    chosen[i] = j
    return chosen


def analyze(photo: Path | None = None, text: str | None = None) -> MealReport:
    fdc_key = os.environ["FDC_API_KEY"]
    foods = identify_foods(photo, text)

    candidates: list[list[dict]] = []
    for food in foods:
        try:
            candidates.append(fetch_fdc_candidates(food.fdc_query, fdc_key))
        except requests.RequestException as exc:
            # One unlucky food must not cost the whole meal; it is reported as unmatched.
            print(f"FDC lookup failed for {food.name!r}: {exc}", file=sys.stderr)
            candidates.append([])

    chosen = select_matches(foods, candidates) if any(candidates) else [None] * len(foods)

    totals: dict[str, float] = {}
    unmatched: list[str] = []
    for food, options, pick in zip(foods, candidates, chosen):
        if pick is None:
            unmatched.append(food.name)
            continue
        match = options[pick]
        food.nutrients = nutrients_for(match, food.portion_grams)
        food.fdc_match = match.get("description")
        for key, value in food.nutrients.items():
            totals[key] = round(totals.get(key, 0) + value, 2)

    return MealReport(foods=foods, totals=totals, unmatched=unmatched)


def _log_path(when: date | None = None) -> Path:
    return DATA_DIR / f"{(when or date.today()).isoformat()}.jsonl"


def daily_totals(when: date | None = None) -> tuple[dict[str, float], int]:
    """Summed nutrients and meal count from a day's log."""
    log = _log_path(when)
    if not log.exists():
        return {}, 0

    totals: dict[str, float] = {}
    meals = 0
    for line in log.read_text().splitlines():
        if not line.strip():
            continue
        meals += 1
        for key, value in json.loads(line)["totals"].items():
            totals[key] = round(totals.get(key, 0) + value, 2)
    return totals, meals


def log_meal(report: MealReport, when: date | None = None) -> dict[str, float]:
    """Append this meal to the day's log and return the running daily totals."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _log_path(when).open("a") as fh:
        fh.write(json.dumps({"foods": [f.name for f in report.foods], "totals": report.totals}) + "\n")
    return daily_totals(when)[0]


def _md(text: str) -> str:
    """Food names come from a model, so neutralise Telegram's Markdown characters."""
    for ch in "_*`[":
        text = text.replace(ch, "\\" + ch)
    return text


def format_report(report: MealReport, daily: dict[str, float] | None = None) -> str:
    lines = ["*This meal*"]
    for food in report.foods:
        if not food.nutrients:
            continue
        n = food.nutrients
        lines.append(
            f"• {_md(food.name)} ~{food.portion_grams:.0f}g — {n['calories']:.0f} kcal, "
            f"{n['protein_g']:.0f}p / {n['carbs_g']:.0f}c / {n['fat_g']:.0f}f"
        )

    t = report.totals
    if not t:
        return "I couldn't match any of these foods to USDA data — try a clearer photo or tell me what's in it."

    lines += [
        "",
        f"*Total:* {t.get('calories', 0):.0f} kcal",
        f"Protein {t.get('protein_g', 0):.0f}g · Carbs {t.get('carbs_g', 0):.0f}g · "
        f"Fat {t.get('fat_g', 0):.0f}g · Fiber {t.get('fiber_g', 0):.0f}g",
    ]

    micros = [
        f"{label} {t[key]:.0f}{unit} ({t[key] / target * 100:.0f}% RDA)"
        if unit != "g"
        else f"{label} {t[key]:.2f}{unit} ({t[key] / target * 100:.0f}% RDA)"
        for key, (target, unit, label) in MICRO_TARGETS.items()
        if t.get(key)
    ]
    if micros:
        lines += ["", "*Micronutrients*"] + [f"• {m}" for m in micros]

    if daily:
        pct = daily.get("calories", 0) / MACRO_TARGETS["calories"] * 100
        protein_pct = daily.get("protein_g", 0) / MACRO_TARGETS["protein_g"] * 100
        lines += [
            "",
            f"*Today so far:* {daily.get('calories', 0):.0f} / {MACRO_TARGETS['calories']} kcal ({pct:.0f}%)",
            f"Protein {daily.get('protein_g', 0):.0f} / {MACRO_TARGETS['protein_g']}g ({protein_pct:.0f}%) · "
            f"Fiber {daily.get('fiber_g', 0):.0f} / {MACRO_TARGETS['fiber_g']}g",
        ]

    if report.unmatched:
        lines += ["", f"_No USDA match (not counted): {_md(', '.join(report.unmatched))}_"]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a meal into macros and micronutrients.")
    parser.add_argument("photo", nargs="?", type=Path, help="Meal photo (omit when using --text)")
    parser.add_argument("--text", help="Describe the meal instead, e.g. '1 scoop whey in 300ml milk'")
    parser.add_argument("--no-log", action="store_true", help="Don't append to the daily log")
    args = parser.parse_args()

    if args.photo is None and not args.text:
        parser.error("give a photo, --text, or both")

    report = analyze(args.photo, args.text)
    daily = None if args.no_log else log_meal(report)
    print(format_report(report, daily))


if __name__ == "__main__":
    main()
