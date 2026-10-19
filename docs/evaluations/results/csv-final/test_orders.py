import csv
import io
import json
from pathlib import Path
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

    def test_customer_example_round_trips(self):
        orders = json.loads(
            Path(__file__).with_name("customer-example.json").read_text(encoding="utf-8")
        )
        rows = list(csv.DictReader(io.StringIO(export_orders(orders), newline="")))
        self.assertEqual(rows, [
            {
                "order_id": "24",
                "address": "12 River Lane, Unit 3",
                "instructions": 'Ask for "Pat"\nUse side entrance',
            },
            {
                "order_id": "25",
                "address": "8 Rue de l'École",
                "instructions": "Call on arrival",
            },
        ])

    def test_special_characters_round_trip(self):
        for value in (
            "",
            "  Keep spaces and a trailing tab\t ",
            '12 River Lane, Unit 3; ask for "Pat"',
            "First line\nSecond line",
            "First line\r\nSecond line",
            "First line\rSecond line",
            "8 Rue de l'École — 東京 🏠",
        ):
            with self.subTest(value=value):
                orders = [{"order_id": 1, "address": value, "instructions": value}]
                rows = list(csv.reader(io.StringIO(export_orders(orders), newline="")))
                self.assertEqual(rows, [
                    ["order_id", "address", "instructions"],
                    ["1", value, value],
                ])

    def test_empty_orders_retains_header(self):
        self.assertEqual(list(csv.reader(io.StringIO(export_orders([])))), [
            ["order_id", "address", "instructions"],
        ])

    def test_missing_fields_and_string_conversion_are_preserved(self):
        rows = list(csv.reader(io.StringIO(export_orders([
            {"order_id": 7},
            {"order_id": None, "address": 42, "instructions": False},
        ]))))
        self.assertEqual(rows[1:], [["7", "", ""], ["None", "42", "False"]])


if __name__ == "__main__":
    unittest.main()
