import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from orders import export_orders


class ExportTests(unittest.TestCase):
    def test_plain_order(self):
        rows = list(csv.reader(io.StringIO(export_orders([
            {"order_id": 1, "address": "42 Oak Road", "instructions": "Ring bell"}
        ]))))
        self.assertEqual(rows, [
            ["order_id", "address", "instructions"],
            ["1", "42 Oak Road", "Ring bell"],
        ])

    def test_customer_download_round_trip(self):
        example = Path(__file__).with_name("customer-example.json")
        orders = json.loads(example.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            download = Path(directory) / "orders.csv"
            with download.open("w", encoding="utf-8", newline="") as stream:
                stream.write(export_orders(orders))
            with download.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(rows, [
            {**order, "order_id": str(order["order_id"])} for order in orders
        ])

    def test_special_characters_and_line_endings_survive(self):
        values = [
            "12 River Lane, Unit 3",
            'Ask for "Pat"',
            "Line one\nLine two",
            "Line one\rLine two",
            "Line one\r\nLine two",
            "  École, 東京 🏠\t ",
            "",
        ]
        for value in values:
            with self.subTest(value=value):
                exported = export_orders([
                    {"order_id": 1, "address": value, "instructions": value}
                ])
                rows = list(csv.reader(io.StringIO(exported, newline="")))
                self.assertEqual(rows, [
                    ["order_id", "address", "instructions"],
                    ["1", value, value],
                ])

    def test_empty_export_has_header(self):
        rows = list(csv.reader(io.StringIO(export_orders([]), newline="")))
        self.assertEqual(rows, [["order_id", "address", "instructions"]])

    def test_missing_fields_and_existing_value_conversion(self):
        exported = export_orders(iter([{"order_id": 0}, {"address": None}]))
        rows = list(csv.reader(io.StringIO(exported, newline="")))
        self.assertEqual(rows, [
            ["order_id", "address", "instructions"],
            ["0", "", ""],
            ["", "None", ""],
        ])


if __name__ == "__main__":
    unittest.main()
