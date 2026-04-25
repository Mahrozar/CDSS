from rules import RULES


def evaluate_rules(data):
    """Forward chaining: evaluate all IF-THEN rules and store active rules."""
    active_rules = []

    for rule in RULES:
        if rule["condition"](data):
            active_rules.append(
                {
                    "rule_id": rule["id"],
                    "level": rule["level"],
                    "if": rule["if_text"],
                    "then": rule["then_text"],
                }
            )

    return active_rules


def resolve_conflict(active_rules):
    """Conflict handling with priority High > Medium > Low."""
    levels = {rule["level"] for rule in active_rules}

    if "High" in levels:
        return "High"
    if "Medium" in levels:
        return "Medium"
    return "Low"
