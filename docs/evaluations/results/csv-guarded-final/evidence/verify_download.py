"""Exercise the fixture's complete local export/download/read workflow."""

import csv
import hashlib
import json
from pathlib import Path
import platform
import sys


workspace = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace))

from orders import export_orders


orders = json.loads((workspace / "customer-example.json").read_text(encoding="utf-8"))
download = workspace / "evidence" / "customer-orders.csv"
with download.open("w", encoding="utf-8", newline="") as stream:
    stream.write(export_orders(orders))
with download.open(encoding="utf-8", newline="") as stream:
    rows = list(csv.DictReader(stream))

expected = [{**order, "order_id": str(order["order_id"])} for order in orders]
assert rows == expected, (rows, expected)

artifacts = ["orders.py", "test_orders.py", "customer-example.json",
             "evidence/verify_download.py", "evidence/customer-orders.csv"]
manifest = {
    "python": platform.python_version(),
    "command": "python3 -I evidence/verify_download.py",
    "result": "PASS",
    "orders_verified": len(rows),
    "assertion": "All parsed fields equal original customer data exactly; IDs stringify.",
    "sha256": {
        name: hashlib.sha256((workspace / name).read_bytes()).hexdigest()
        for name in artifacts
    },
}
(workspace / "evidence" / "verification.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
print(f"PASS: downloaded and read {len(rows)} orders; all customer fields match exactly.")
print(f"Python {manifest['python']}; UTF-8 download: {download}")
