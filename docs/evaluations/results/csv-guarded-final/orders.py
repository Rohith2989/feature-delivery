"""Small download adapter used by the evaluation application."""

import csv
import io


def export_orders(orders):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    fields = ("order_id", "address", "instructions")
    writer.writerow(fields)
    for order in orders:
        writer.writerow(str(order.get(key, "")) for key in fields)
    return output.getvalue()
