import unittest

from alerts import visible_alerts


class VisibleAlertsTests(unittest.TestCase):
    def test_only_current_owners_unarchived_alerts_are_visible(self):
        alerts = [
            {"id": "active", "owner": "alice", "archived": False},
            {"id": "archived", "owner": "alice", "archived": True},
            {"id": "legacy", "owner": "alice"},
            {"id": "other", "owner": "bob", "archived": False},
            {"id": "other-archived", "owner": "bob", "archived": True},
        ]

        self.assertEqual(
            [alert["id"] for alert in visible_alerts(alerts, "alice")],
            ["active", "legacy"],
        )

    def test_empty_list_is_visible_as_empty(self):
        self.assertEqual(visible_alerts([], "alice"), [])

    def test_missing_owner_still_fails(self):
        with self.assertRaisesRegex(ValueError, "Owner is required"):
            visible_alerts([], None)


if __name__ == "__main__":
    unittest.main()
