# utils/validators.py

"""
validators.py
--------------
This module enforces dietary rules, allergies, and content cleanup
AFTER the LLM generates meal plans or shopping lists.

It ensures:
- No meat/fish/egg items when user is vegetarian.
- No dairy/egg/honey when user is vegan.
- No ingredients matching allergy list.
- Automatic correction or annotation of invalid items.
- Safe handling of None values.
"""

import re


# -------------------------------------------------------------
# Normalizers
# -------------------------------------------------------------
def _norm(text):
    """Safety-normalize any text."""
    if not text:
        return ""
    return str(text).lower().strip()


def _contains(word_list, text):
    """Return True if any banned word appears as a word or substring."""
    t = _norm(text)
    return any(w in t for w in word_list)


# -------------------------------------------------------------
# Lists of banned items
# -------------------------------------------------------------
MEAT_WORDS = [
    "chicken", "fish", "salmon", "tuna", "prawn", "shrimp", "beef",
    "mutton", "pork", "lamb", "turkey", "egg", "eggs", "steak", "ham"
]

DAIRY_WORDS = [
    "milk", "cheese", "butter", "yogurt", "cream", "paneer",
    "ghee", "curd", "kefir"
]

SEAFOOD_WORDS = [
    "crab", "lobster", "clam", "oyster", "squid"
]

ALL_NON_VEG = MEAT_WORDS + SEAFOOD_WORDS


# -------------------------------------------------------------
# Replacement utility
# -------------------------------------------------------------
def _mark(text, word, reason):
    """Annotate a forbidden word with a removal remark."""
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    return pattern.sub(f"{word} (REMOVE: {reason})", text)


# -------------------------------------------------------------
# Core Conditioner
# -------------------------------------------------------------
def validate_meal_plan(text: str, prefs: dict) -> str:
    """
    Cleans up LLM output according to preferences.
    Does NOT try to rewrite entire meals—only removes or annotates violations.

    Arguments:
        text: LLM output
        prefs: LLM-extracted user preferences
    """
    if not text:
        return ""

    out = text

    # ---------- Normalize preference fields ----------
    diet = _norm(prefs.get("diet_type"))
    allergies = prefs.get("allergies", []) or []
    allergies = [_norm(a) for a in allergies if a]

    # -------------------------------------------------
    # 1. ENFORCE VEGETARIAN
    # -------------------------------------------------
    if diet in ("veg", "vegetarian"):
        for w in ALL_NON_VEG:
            if w in out.lower():
                out = _mark(out, w, "user is vegetarian")

    # -------------------------------------------------
    # 2. ENFORCE VEGAN
    # -------------------------------------------------
    if diet == "vegan":
        # remove meat, fish, dairy, honey
        banned = ALL_NON_VEG + DAIRY_WORDS + ["honey"]
        for w in banned:
            if w in out.lower():
                out = _mark(out, w, "user is vegan")

    # -------------------------------------------------
    # 3. ALLERGY ENFORCEMENT
    # -------------------------------------------------
    for allergen in allergies:
        if allergen and allergen in out.lower():
            out = _mark(out, allergen, "allergy")

    # -------------------------------------------------
    # 4. Minor cleanup (avoid duplicate REMOVE tags)
    # -------------------------------------------------
    out = re.sub(r"\(REMOVE: [^)]+\)\s*\(REMOVE: [^)]+\)", "(REMOVE)", out)
    out = re.sub(r"\s{2,}", " ", out)

    return out


# --------------------------------------------------------------------
# Optional: strict validator for shopping list dictionaries (future)
# --------------------------------------------------------------------
def sanitize_shopping_list(items, prefs):
    """
    Enforces dietary rules inside structured shopping lists.
    items = list of dicts: {category, item, quantity, notes}

    This ensures:
    - Non-veg ingredients are flagged or removed.
    - Allergies flagged.
    """
    cleaned = []
    diet = _norm(prefs.get("diet_type"))
    allergies = [_norm(a) for a in prefs.get("allergies", []) or []]

    for row in items:
        item = _norm(row.get("item", ""))
        notes = row.get("notes", "")

        flagged = False
        reason_list = []

        # Vegetarian enforcement
        if diet in ("veg", "vegetarian") and _contains(ALL_NON_VEG, item):
            flagged = True
            reason_list.append("non-veg ingredient (vegetarian user)")

        # Vegan enforcement
        if diet == "vegan":
            if _contains(ALL_NON_VEG + DAIRY_WORDS + ["honey"], item):
                flagged = True
                reason_list.append("non-vegan ingredient (vegan user)")

        # Allergy enforcement
        for a in allergies:
            if a in item:
                flagged = True
                reason_list.append(f"contains allergen: {a}")

        # If flagged → modify the item
        if flagged:
            row["notes"] = (notes + " | REMOVE: " + ", ".join(reason_list)).strip()

        cleaned.append(row)

    return cleaned
