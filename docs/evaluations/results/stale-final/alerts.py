def visible_alerts(alerts, owner):
    if owner is None:
        raise ValueError("Owner is required")
    return [a for a in alerts if a["owner"] == owner and not a.get("archived", False)]
