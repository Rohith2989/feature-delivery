"""Small download adapter used by the evaluation application."""


def export_orders(orders):
    rows = ["order_id,address,instructions"]
    for order in orders:
        rows.append(",".join(str(order.get(key, "")) for key in (
            "order_id", "address", "instructions"
        )))
    return "\n".join(rows) + "\n"
