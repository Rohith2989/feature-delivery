import csv
import io
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


if __name__ == "__main__":
    unittest.main()
