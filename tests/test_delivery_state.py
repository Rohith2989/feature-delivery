"""Offline consistency checks, not application acceptance or remote-system tests."""

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/feature-delivery/scripts/delivery_state.py"
SPEC = importlib.util.spec_from_file_location("delivery_state", SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)

COMMIT = "a" * 40
OTHER_COMMIT = "b" * 40
SCOPE = "Password recovery acceptance"
NOW = datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)


class DeliveryStateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.state = self.root / "state.json"
        (self.root / "evidence").mkdir()
        (self.root / "evidence/check.txt").write_text("Observed expected behavior; limited to this scope.\n", encoding="utf-8")
        self.clock = patch.object(helper, "now_utc", return_value=NOW)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def run_cli(self, *arguments):
        with redirect_stdout(io.StringIO()) as output:
            code = helper.main(list(arguments))
        return code, json.loads(output.getvalue())

    def initialize(self, *gates):
        arguments = ["init", "--state", str(self.state), "--candidate", COMMIT, "--scope", SCOPE]
        for gate in gates or ("tests=local@developer",):
            arguments.extend(("--gate", gate))
        return self.run_cli(*arguments)

    def record(self, **overrides):
        options = {"candidate": COMMIT, "gate": "tests", "level": "local", "status": "passed",
                   "scope": SCOPE, "environment": "developer", "observed-at": helper.iso(NOW),
                   "artifact": "evidence/check.txt", "note": "Observed scope; not independent approval."}
        options.update(overrides)
        arguments = ["record", "--state", str(self.state)]
        for key, value in options.items():
            arguments.extend(("--" + key.replace("_", "-"), value))
        return self.run_cli(*arguments)

    def check(self, commit=COMMIT, age="24"):
        return self.run_cli("check", "--state", str(self.state), "--candidate", commit,
                            "--max-age-hours", age)

    def test_initialized_checkpoint_has_no_implicit_release_approval(self):
        code, output = self.initialize()
        self.assertEqual(code, 0)
        self.assertIn("does not prove live behavior", output["notice"])
        state = json.loads(self.state.read_text())
        self.assertEqual(len(state["gates"]), 1)
        self.assertEqual(state["gates"][0]["level"], "local")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("no recorded evidence", output["issues"][0])

    def test_init_never_overwrites_an_existing_checkpoint(self):
        self.initialize()
        original = self.state.read_bytes()
        self.assertEqual(self.initialize()[0], 2)
        self.assertEqual(self.state.read_bytes(), original)

    def test_init_refuses_a_racing_noncooperating_creator(self):
        real_link = os.link

        def racing_link(source, destination):
            self.state.write_bytes(b"new external state must survive")
            return real_link(source, destination)

        with patch.object(helper.os, "link", side_effect=racing_link):
            self.assertEqual(self.initialize()[0], 2)
        self.assertEqual(self.state.read_bytes(), b"new external state must survive")
        self.assertEqual(list(self.root.glob(".delivery-state-*")), [])

    def test_fresh_local_receipt_is_only_recorded_gates_consistent(self):
        self.initialize()
        self.assertEqual(self.record()[0], 0)
        code, output = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(output["result"], "recorded gates consistent")
        self.assertIn("independent acceptance", output["notice"])
        event = json.loads(self.state.read_text())["events"][0]
        self.assertEqual(event["artifacts"][0]["bytes"], (self.root / "evidence/check.txt").stat().st_size)

    def test_64_character_source_identity_supported(self):
        self.assertEqual(self.run_cli("init", "--state", str(self.state), "--candidate", "c" * 64,
                                     "--scope", SCOPE, "--gate", "lint=local@developer")[0], 0)

    def test_ambiguous_or_malformed_candidate_rejected(self):
        for value in ("abc1234", "main", "A" * 40, "a" * 41):
            with self.subTest(value=value):
                code, _ = self.run_cli("init", "--state", str(self.state), "--candidate", value,
                                       "--scope", SCOPE, "--gate", "test=local@developer")
                self.assertEqual(code, 2)
                self.assertFalse(self.state.exists())

    def test_duplicate_or_invalid_gate_rejected_before_creation(self):
        for gates in (("test=local@developer", "test=live@production"),
                      ("test=remote@production",), ("test=local",), ("../test=local@developer",)):
            with self.subTest(gates=gates):
                self.assertEqual(self.initialize(*gates)[0], 2)
                self.assertFalse(self.state.exists())

    def test_source_change_requires_a_new_checkpoint(self):
        self.initialize()
        original = self.state.read_bytes()
        self.assertEqual(self.record(candidate=OTHER_COMMIT)[0], 2)
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(self.check(OTHER_COMMIT)[0], 1)

    def test_evidence_level_environment_and_scope_are_exact(self):
        self.initialize()
        for change in ({"level": "live"}, {"environment": "production"}, {"scope": "Different scope"},
                       {"gate": "missing"}):
            with self.subTest(change=change):
                self.assertEqual(self.record(**change)[0], 2)
        self.assertEqual(json.loads(self.state.read_text())["events"], [])

    def test_unknown_failed_and_partial_do_not_reuse_previous_pass(self):
        self.initialize()
        self.record()
        for status in ("unknown", "partial", "failed"):
            with self.subTest(status=status):
                self.assertEqual(self.record(status=status)[0], 0)
                code, output = self.check()
                self.assertEqual(code, 1)
                self.assertIn(status, output["issues"][0])
        events = json.loads(self.state.read_text())["events"]
        self.assertEqual([event["status"] for event in events], ["passed", "unknown", "partial", "failed"])

    def test_stale_observation_cannot_be_refreshed_by_recording_it_now(self):
        self.initialize()
        self.record(**{"observed-at": helper.iso(NOW - timedelta(hours=25))})
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("stale" in issue for issue in output["issues"]))

    def test_older_pass_cannot_clear_a_newer_unknown_observation(self):
        self.initialize()
        self.assertEqual(self.record(status="unknown")[0], 0)
        original = self.state.read_bytes()
        code, _ = self.record(**{"observed-at": helper.iso(NOW - timedelta(minutes=10))})
        self.assertEqual(code, 2)
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(self.check()[0], 1)

    def test_tied_pass_cannot_clear_uncertainty_but_later_observation_can(self):
        self.initialize()
        self.assertEqual(self.record(status="failed")[0], 0)
        original = self.state.read_bytes()
        self.assertEqual(self.record()[0], 2)
        self.assertEqual(self.state.read_bytes(), original)
        later = NOW + timedelta(microseconds=100)
        with patch.object(helper, "now_utc", return_value=later):
            self.assertEqual(self.record(**{"observed-at": helper.iso(later)})[0], 0)
            self.assertEqual(self.check()[0], 0)

    def test_imported_state_cannot_hide_newer_failure_behind_older_pass(self):
        self.initialize()
        self.record(status="failed")
        state = json.loads(self.state.read_text())
        stale = dict(state["events"][0], sequence=2, status="passed",
                     observed_at=helper.iso(NOW - timedelta(minutes=10)))
        state["events"].append(stale)
        self.state.write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(self.check()[0], 2)

    def test_future_or_timezone_ambiguous_observations_rejected(self):
        self.initialize()
        for observed in (helper.iso(NOW + timedelta(seconds=61)), "2026-01-02", "2026-01-02Z",
                         "2026-01-02T12:00:00+01:00", "nonsense"):
            with self.subTest(observed=observed):
                self.assertEqual(self.record(**{"observed-at": observed})[0], 2)

    def test_bad_maximum_ages_fail_closed(self):
        self.initialize()
        self.record()
        for age in ("nan", "inf", "-1", "0"):
            with self.subTest(age=age):
                self.assertEqual(self.check(age=age)[0], 2)

    def test_changed_and_missing_artifacts_need_attention(self):
        self.initialize()
        self.record()
        artifact = self.root / "evidence/check.txt"
        artifact.write_text("Different result.\n", encoding="utf-8")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("differ" in issue for issue in output["issues"]))
        artifact.unlink()
        self.assertEqual(self.check()[0], 1)

    def test_deployed_and_live_require_same_actual_deployment_identity(self):
        self.initialize("release=deployed@staging", "smoke=live@staging")
        common = {"environment": "staging", "deployment_id": "image:sha256:first"}
        self.assertEqual(self.record(gate="release", level="deployed", **common)[0], 0)
        self.assertEqual(self.record(gate="smoke", level="live", **dict(common, deployment_id="image:sha256:second"))[0], 0)
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("disagree" in issue for issue in output["issues"]))
        self.assertEqual(self.record(gate="smoke", level="live", **common)[0], 0)
        self.assertEqual(self.check()[0], 0)

    def test_multiservice_deployments_pair_identity_per_component(self):
        self.initialize("api-release=deployed@staging/api", "api-smoke=live@staging/api",
                        "worker-release=deployed@staging/worker", "worker-smoke=live@staging/worker")
        for component in ("api", "worker"):
            for name, level in (("release", "deployed"), ("smoke", "live")):
                self.assertEqual(self.record(gate=component + "-" + name, level=level,
                    environment="staging", component=component, deployment_id="image:" + component)[0], 0)
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(self.record(gate="api-smoke", level="live", environment="staging",
            component="worker", deployment_id="image:worker")[0], 2)
        self.assertEqual(self.record(gate="worker-smoke", level="live", environment="staging",
            component="worker", deployment_id="image:wrong-worker")[0], 0)
        self.assertEqual(self.check()[0], 1)

    def test_deployment_identity_is_mandatory_only_for_nonlocal_gates(self):
        self.initialize("release=deployed@staging")
        self.assertEqual(self.record(gate="release", level="deployed", environment="staging")[0], 2)
        self.assertEqual(json.loads(self.state.read_text())["events"], [])

    def test_local_receipt_cannot_claim_a_deployment_identity(self):
        self.initialize()
        self.assertEqual(self.record(deployment_id="release:example")[0], 2)

    def test_different_environments_can_have_different_deployments(self):
        self.initialize("staging=live@staging", "production=live@production")
        for environment in ("staging", "production"):
            self.assertEqual(self.record(gate=environment, level="live", environment=environment,
                                         deployment_id="release:" + environment)[0], 0)
        self.assertEqual(self.check()[0], 0)

    def test_artifact_path_traversal_and_ambiguous_paths_rejected(self):
        self.initialize()
        for path in ("../outside.txt", "evidence/../../outside.txt", str(self.root / "evidence/check.txt"),
                     "C:/outside.txt", "evidence\\check.txt", "evidence//check.txt", "./evidence/check.txt",
                     "evidence/check.txt\x00", "evidence/./check.txt"):
            with self.subTest(path=path):
                self.assertEqual(self.record(artifact=path)[0], 2)
        self.assertEqual(json.loads(self.state.read_text())["events"], [])

    def test_artifact_symlinks_and_symlinked_directories_rejected(self):
        self.initialize()
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "outside.txt"
            external.write_text("Never follow this private file.\n", encoding="utf-8")
            try:
                (self.root / "leaf-link.txt").symlink_to(external)
                (self.root / "directory-link").symlink_to(Path(outside), target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable for this account/platform.")
            with patch.object(helper.os, "open", wraps=os.open) as opener:
                self.assertEqual(self.record(artifact="leaf-link.txt")[0], 2)
                self.assertEqual(self.record(artifact="directory-link/outside.txt")[0], 2)
                opened = [str(call.args[0]) for call in opener.call_args_list]
                self.assertNotIn(str(external), opened)
        self.assertEqual(json.loads(self.state.read_text())["events"], [])

    def test_empty_artifact_is_not_evidence(self):
        self.initialize()
        (self.root / "empty.txt").touch()
        self.assertEqual(self.record(artifact="empty.txt")[0], 2)

    def test_oversized_artifact_is_rejected_without_reading_bytes(self):
        self.initialize()
        with (self.root / "too-large.txt").open("wb") as stream:
            stream.truncate(helper.MAX_ARTIFACT_BYTES + 1)
        self.assertEqual(self.record(artifact="too-large.txt")[0], 2)

    def test_artifact_replaced_by_symlink_invalidates_old_receipt(self):
        self.initialize()
        self.record()
        artifact = self.root / "evidence/check.txt"
        artifact.unlink()
        try:
            artifact.symlink_to(self.state)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable for this account/platform.")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("symlink" in issue for issue in output["issues"]))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFOs are not available on this platform.")
    def test_fifo_rejected_without_opening_it(self):
        self.initialize()
        os.mkfifo(self.root / "pipe")
        self.assertEqual(self.record(artifact="pipe")[0], 2)

    def test_state_itself_cannot_be_evidence(self):
        self.initialize()
        self.assertEqual(self.record(artifact="state.json")[0], 2)

    def test_existing_lock_is_never_removed_or_treated_as_stale(self):
        self.initialize()
        lock = self.root / "state.json.lock"
        lock.write_text("owned by another process\n", encoding="utf-8")
        original = self.state.read_bytes()
        self.assertEqual(self.record()[0], 2)
        self.assertEqual(self.check()[0], 2)
        self.assertEqual(lock.read_text(), "owned by another process\n")
        self.assertEqual(self.state.read_bytes(), original)

    def test_malformed_state_is_never_overwritten_or_truncated(self):
        self.initialize()
        self.state.write_bytes(b'{"schema_version":')
        original = self.state.read_bytes()
        self.assertEqual(self.record()[0], 2)
        self.assertEqual(self.state.read_bytes(), original)
        self.assertFalse((self.root / "state.json.lock").exists())

    def test_state_symlink_is_not_followed(self):
        target = self.root / "external-state.json"
        target.write_text("private unrelated state", encoding="utf-8")
        try:
            self.state.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable for this account/platform.")
        self.assertEqual(self.initialize()[0], 2)
        self.assertEqual(self.check()[0], 2)
        self.assertEqual(target.read_text(), "private unrelated state")

    def test_oversized_state_is_refused_without_replacement(self):
        self.initialize()
        with self.state.open("wb") as stream:
            stream.truncate(helper.MAX_STATE_BYTES + 1)
        self.assertEqual(self.record()[0], 2)
        self.assertEqual(self.state.stat().st_size, helper.MAX_STATE_BYTES + 1)

    def test_future_checkpoint_and_recording_times_need_attention(self):
        self.initialize()
        self.record()
        state = json.loads(self.state.read_text())
        future = helper.iso(NOW + timedelta(minutes=5))
        state["created_at"] = future
        state["events"][0]["recorded_at"] = future
        self.state.write_text(json.dumps(state), encoding="utf-8")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any("creation timestamp" in issue for issue in output["issues"]))
        self.assertTrue(any("recording timestamp" in issue for issue in output["issues"]))

    def test_unsupported_fields_and_invalid_sequences_are_refused(self):
        self.initialize()
        self.record()
        valid = json.loads(self.state.read_text())
        variants = [dict(valid, schema_version=2), dict(valid, approval="granted"),
                    dict(valid, events=[dict(valid["events"][0], sequence=3)]),
                    dict(valid, events=[dict(valid["events"][0], candidate=OTHER_COMMIT)]),
                    dict(valid, events=[dict(valid["events"][0], artifacts=[{"path": "../outside.txt",
                                                                         "sha256": "a" * 64, "bytes": 1}])])]
        for state in variants:
            with self.subTest(state=state):
                self.state.write_text(json.dumps(state), encoding="utf-8")
                original = self.state.read_bytes()
                self.assertEqual(self.record()[0], 2)
                self.assertEqual(self.state.read_bytes(), original)

    def test_failed_atomic_replace_preserves_existing_state_and_cleans_temp(self):
        self.initialize()
        original = self.state.read_bytes()
        with patch.object(helper.os, "replace", side_effect=OSError("simulated write failure")):
            self.assertEqual(self.record()[0], 2)
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(list(self.root.glob(".delivery-state-*")), [])
        self.assertFalse((self.root / "state.json.lock").exists())

    def test_error_output_does_not_dump_notes_or_artifact_contents(self):
        self.initialize()
        code, output = self.record(artifact="missing.txt", note="PRIVATE_NOTE_DO_NOT_LOG")
        self.assertEqual(code, 2)
        self.assertNotIn("PRIVATE_NOTE_DO_NOT_LOG", json.dumps(output))


if __name__ == "__main__":
    unittest.main()
