# ─────────────────────────────────────────────
#  CARD DATABASE
#  reward_rate = fraction of transaction value
#  monthly_cap = max cashback/reward value per month (INR equivalent)
#  acceptance  = "high" | "medium" | "low"  (for offline fallback)
# ─────────────────────────────────────────────

CARDS = {
    "hdfc_millennia": {
        "display_name": "HDFC Millennia",
        "rewards": {
            "online":   0.05,
            "dining":   0.05,
            "grocery":  0.05,
            "fuel":     0.01,
            "travel":   0.01,
            "utility":  0.01,
            "default":  0.01,
        },
        "monthly_cap": 1000,
        "acceptance": "high",
        "note": "5% cashback on online, dining, grocery (Swiggy, Amazon, BigBasket)",
    },
    "axis_flipkart": {
        "display_name": "Axis Flipkart",
        "rewards": {
            "online":   0.05,
            "dining":   0.04,
            "grocery":  0.04,
            "fuel":     0.01,
            "travel":   0.04,
            "utility":  0.015,
            "default":  0.015,
        },
        "monthly_cap": None,
        "acceptance": "high",
        "note": "5% on Flipkart/Myntra, 4% on Swiggy/Uber/BigBasket, no cap",
    },
    "sbi_simplyclick": {
        "display_name": "SBI SimplyCLICK",
        "rewards": {
            "online":   0.025,
            "dining":   0.005,
            "grocery":  0.005,
            "fuel":     0.005,
            "travel":   0.025,
            "utility":  0.005,
            "default":  0.005,
        },
        "monthly_cap": 167,
        "acceptance": "high",
        "note": "10x points on Amazon/Cleartrip but Rs.2,000/year reward cap",
    },
    "axis_magnus": {
        "display_name": "Axis Magnus",
        "rewards": {
            "online":   0.036,
            "dining":   0.036,
            "grocery":  0.036,
            "fuel":     0.01,
            "travel":   0.036,
            "utility":  0.005,
            "default":  0.036,
        },
        "monthly_cap": 9000,
        "acceptance": "high",
        "note": "Premium card — consistent 3.6% on most spends, lounge access",
    },
    "amex_mrcc": {
        "display_name": "Amex MRCC",
        "rewards": {
            "online":   0.025,
            "dining":   0.025,
            "grocery":  0.025,
            "fuel":     0.005,
            "travel":   0.005,
            "utility":  0.005,
            "default":  0.005,
        },
        "monthly_cap": 375,
        "acceptance": "low",
        "note": "Good online rewards but low offline acceptance in India",
    },
    "hdfc_regalia": {
        "display_name": "HDFC Regalia",
        "rewards": {
            "online":   0.013,
            "dining":   0.013,
            "grocery":  0.013,
            "fuel":     0.01,
            "travel":   0.013,
            "utility":  0.013,
            "default":  0.013,
        },
        "monthly_cap": None,
        "acceptance": "high",
        "note": "Best for travel — lounge access, consistent 1.3% on all spends",
    },
}


# ─────────────────────────────────────────────
#  DECISION ENGINE
# ─────────────────────────────────────────────

def recommend(category, amount, user_cards, caps_used=None):
    if caps_used is None:
        caps_used = {}

    cat = category.lower().strip()
    if cat not in ["online", "dining", "grocery", "fuel", "travel", "utility"]:
        cat = "default"
        category_known = False
    else:
        category_known = True

    candidates = []

    for card_id in user_cards:
        card = CARDS.get(card_id)
        if not card:
            continue

        rate     = card["rewards"].get(cat, card["rewards"]["default"])
        cashback = round(amount * rate, 2)

        cap          = card["monthly_cap"]
        already_used = caps_used.get(card_id, 0)
        cap_warning  = None
        cap_hit      = False

        if cap is not None:
            remaining_cap = cap - already_used
            if remaining_cap <= 0:
                cap_hit = True
                cashback = 0
                cap_warning = f"Monthly cap of Rs.{cap} fully used — no reward this transaction"
            elif cashback > remaining_cap:
                cashback = round(remaining_cap, 2)
                cap_warning = f"Partial reward — only Rs.{remaining_cap} left in monthly cap"

        acceptance_note = None
        if card["acceptance"] == "low":
            acceptance_note = "Low merchant acceptance in India — may be declined offline"

        candidates.append({
            "card_id":         card_id,
            "display_name":    card["display_name"],
            "rate":            rate,
            "cashback":        cashback,
            "cap_hit":         cap_hit,
            "cap_warning":     cap_warning,
            "acceptance":      card["acceptance"],
            "acceptance_note": acceptance_note,
            "note":            card["note"],
        })

    if not candidates:
        return {
            "recommendation": None,
            "reason": "None of the selected cards are in our database",
            "confidence": "low",
        }

    def score(c):
        s = c["cashback"]
        if c["cap_hit"]:       s -= 10000
        if c["acceptance"] == "low": s -= 5
        return s

    ranked = sorted(candidates, key=score, reverse=True)
    best   = ranked[0]

    fallback_chain = [
        {
            "card":     c["display_name"],
            "cashback": f"Rs.{c['cashback']}",
            "rate":     f"{round(c['rate']*100, 1)}%",
            "note":     c["cap_warning"] or c["acceptance_note"] or c["note"],
        }
        for c in ranked[:3]
    ]

    if not category_known:
        confidence = "low — category unknown, using base rates"
    elif best["cap_hit"]:
        confidence = "low — best card cap hit, recommending next best"
    elif best["cap_warning"]:
        confidence = "medium — partial reward due to cap"
    else:
        confidence = "high"

    rec_line = f"Use {best['display_name']} — earn Rs.{best['cashback']} back ({round(best['rate']*100,1)}% on {category})"
    if best["cap_warning"]:
        rec_line += f". Note: {best['cap_warning']}"
    if best["acceptance_note"]:
        rec_line += f". Warning: {best['acceptance_note']}"

    return {
        "recommendation": rec_line,
        "card_id":        best["card_id"],
        "card_name":      best["display_name"],
        "cashback":       best["cashback"],
        "rate":           f"{round(best['rate']*100, 1)}%",
        "confidence":     confidence,
        "category_used":  cat,
        "fallback_chain": fallback_chain,
    }
