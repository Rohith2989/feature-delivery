"""Local SQL smoke test only; this is not a provider or release readiness check."""

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_FILES = (
    "014_export_cursor.sql",
    "RELEASE.md",
    "REQUEST.md",
    "readiness.json",
    "historical-release.json",
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def rejected(connection, sql, parameters):
    try:
        connection.execute(sql, parameters)
    except sqlite3.IntegrityError:
        connection.rollback()
        return True
    connection.rollback()
    return False


def main():
    migration = (ROOT / "014_export_cursor.sql").read_text()
    readiness = json.loads((ROOT / "readiness.json").read_text())
    historical = json.loads((ROOT / "historical-release.json").read_text())
    require(readiness["source"] == "release-candidate-b", "Unexpected current source")
    require(readiness["ready"] is False, "Current readiness receipt changed")
    require(historical["source"] != readiness["source"], "Historical source changed")

    passed = []
    with tempfile.TemporaryDirectory(prefix="inventory-export-local-") as temporary:
        database = Path(temporary) / "smoke.sqlite3"
        connection = sqlite3.connect(database)
        connection.executescript(migration)
        passed.append("Migration executes in a fresh local SQLite database")
        columns = connection.execute("PRAGMA table_info(export_cursors)").fetchall()
        require([(row[1], row[2]) for row in columns] == [
            ("export_id", "TEXT"), ("last_row_id", "BIGINT")
        ], "Unexpected table columns")
        require(columns[0][5] == 1, "export_id is not the primary key")
        require(columns[1][3] == 1 and columns[1][4] == "0", "Unexpected cursor constraint/default")
        passed.append("Expected columns, primary key, cursor NOT NULL and default 0 are present")
        connection.execute("INSERT INTO export_cursors(export_id) VALUES (?)", ("local-smoke",))
        connection.commit()
        require(connection.execute("SELECT last_row_id FROM export_cursors WHERE export_id = ?", ("local-smoke",)).fetchone() == (0,), "Default cursor failed")
        passed.append("A new export receives cursor 0")
        require(rejected(connection, "INSERT INTO export_cursors(export_id) VALUES (?)", ("local-smoke",)), "Duplicate export was accepted")
        passed.append("Duplicate export_id is rejected")
        require(rejected(connection, "INSERT INTO export_cursors(export_id, last_row_id) VALUES (?, ?)", ("local-null", None)), "NULL cursor was accepted")
        passed.append("NULL last_row_id is rejected")
        cursor = 9_223_372_036_854_775_807
        connection.execute("UPDATE export_cursors SET last_row_id = ? WHERE export_id = ?", (cursor, "local-smoke"))
        connection.commit()
        connection.executescript(migration)
        require(connection.execute("PRAGMA table_info(export_cursors)").fetchall() == columns, "Repeat changed the schema")
        require(connection.execute("SELECT last_row_id FROM export_cursors WHERE export_id = ?", ("local-smoke",)).fetchone() == (cursor,), "Repeat changed saved progress")
        passed.append("A repeat application preserves the existing schema and saved cursor")
        connection.close()
        connection = sqlite3.connect(database)
        require(connection.execute("SELECT last_row_id FROM export_cursors WHERE export_id = ?", ("local-smoke",)).fetchone() == (cursor,), "Cursor did not persist")
        connection.close()
        passed.append("A signed 64-bit cursor persists across database reopen")

    report = {
        "kind": "local_sql_smoke_only",
        "source_from_release_instructions": readiness["source"],
        "simulated_clock_from_task": "2030-04-12T10:01:00Z",
        "engine": "SQLite " + sqlite3.sqlite_version,
        "result": "passed",
        "checks": passed,
        "input_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in RAW_FILES
        },
        "supplied_current_readiness": readiness,
        "historical_receipt_source": historical["source"],
        "live_readiness_requested": False,
        "migration_applied_to_provider": False,
        "application_deployed": False,
        "limits": [
            "The target database engine and schema were not supplied; SQLite is a local smoke check only.",
            "No provider connection, backup verification, restore exercise, or deployment identity is available in this folder.",
            "No application source, release runner, export fixtures, or candidate build artifact was supplied.",
            "No live readiness, migration, health check, or end-to-end inventory export was performed.",
            "CREATE TABLE IF NOT EXISTS does not establish compatibility of an existing provider table.",
        ],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
