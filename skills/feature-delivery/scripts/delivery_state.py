#!/usr/bin/env python3
"""Optional, offline evidence index. Consistency is not release approval.

Python 3.10+, standard library only. Evidence paths are relative to the state
directory, which should be private and ignored by Git (normally .delivery/).
This program never runs tests, deploys software, or verifies a remote system.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile


SCHEMA_VERSION = 1
MAX_STATE_BYTES = 5 * 1024 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
LEVELS = ("local", "deployed", "live")
STATUSES = ("passed", "failed", "partial", "unknown")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
DISCLAIMER = (
    "This checks recorded declarations and local artifact bytes only; it does "
    "not prove live behavior, authorize a release, or replace independent acceptance."
)


class EvidenceError(Exception):
    """A bounded input or consistency error safe to report without file contents."""


def now_utc():
    return datetime.now(timezone.utc)


def timestamp(value):
    if not isinstance(value, str) or len(value) > 40:
        raise EvidenceError("Timestamp must be an ISO 8601 UTC string ending in Z.")
    try:
        if not value.endswith("Z"):
            raise ValueError()
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
        if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
            raise ValueError()
    except ValueError as exc:
        raise EvidenceError("Timestamp must be an ISO 8601 UTC string ending in Z.") from exc
    return parsed


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def bounded_text(value, field, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise EvidenceError(f"{field} must contain 1 to {limit} characters.")
    if any(ord(character) < 32 and character not in "\n\t" for character in value):
        raise EvidenceError(f"{field} contains control characters.")
    return value


def candidate(value):
    if not isinstance(value, str) or not COMMIT.fullmatch(value):
        raise EvidenceError("Candidate must be a full lowercase 40- or 64-character commit hash.")
    return value


def gate_spec(value, scope):
    """Parse NAME=LEVEL@ENVIRONMENT[/COMPONENT]; no implicit release gates."""
    try:
        name, remainder = value.split("=", 1)
        level, environment = remainder.split("@", 1)
        environment, separator, component = environment.partition("/")
        if not separator:
            component = "default"
    except ValueError as exc:
        raise EvidenceError("Gate must use NAME=LEVEL@ENVIRONMENT[/COMPONENT].") from exc
    if any(not IDENTIFIER.fullmatch(value) for value in (name, environment, component)):
        raise EvidenceError("Gate, environment, and component names use letters, numbers, '.', '_' or '-'.")
    if level not in LEVELS:
        raise EvidenceError("Gate level must be local, deployed, or live.")
    return {"name": name, "level": level, "environment": environment,
            "component": component, "scope": scope}


def relative_artifact(value):
    if (not isinstance(value, str) or not value or len(value) > 500 or
            any(ord(character) < 32 for character in value)):
        raise EvidenceError("Artifact path must be a nonempty relative POSIX path.")
    path = PurePosixPath(value)
    if (path.is_absolute() or "\\" in value or ":" in value or
            any(part in ("", ".", "..") for part in value.split("/"))):
        raise EvidenceError("Artifact paths cannot be absolute, ambiguous, or traverse directories.")
    return path


def artifact_receipt(root, relative, forbidden=()):
    path = relative_artifact(relative)
    current = root
    for part in path.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise EvidenceError("An artifact is missing or inaccessible.") from exc
        if stat.S_ISLNK(info.st_mode):
            raise EvidenceError("Artifact paths cannot contain symlinks.")
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARTIFACT_BYTES:
        raise EvidenceError("Artifacts must be regular files no larger than 64 MiB.")
    if current in forbidden:
        raise EvidenceError("State and lock files cannot be used as evidence artifacts.")
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NONBLOCK", 0))
    try:
        if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"):
            # Pin each directory on POSIX so a concurrent parent symlink swap
            # cannot redirect evidence reads outside the configured root.
            directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            directory = os.open(root, directory_flags)
            try:
                for part in path.parts[:-1]:
                    following = os.open(part, directory_flags, dir_fd=directory)
                    os.close(directory)
                    directory = following
                descriptor = os.open(path.parts[-1], flags, dir_fd=directory)
            finally:
                os.close(directory)
        else:
            descriptor = os.open(current, flags)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_ARTIFACT_BYTES:
                raise EvidenceError("Artifacts must be regular files no larger than 64 MiB.")
            if (before.st_dev, before.st_ino) != (info.st_dev, info.st_ino):
                raise EvidenceError("Artifact changed while being opened.")
            digest = hashlib.sha256()
            size = 0
            while chunk := stream.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_ARTIFACT_BYTES:
                    raise EvidenceError("Artifact exceeded the 64 MiB bound while reading.")
                digest.update(chunk)
            after = os.fstat(stream.fileno())
        latest = current.lstat()
    except OSError as exc:
        raise EvidenceError("An artifact is missing, inaccessible, or changed during inspection.") from exc
    identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    if identity(before) != identity(after) or identity(after) != identity(latest):
        raise EvidenceError("Artifact changed during inspection.")
    if size == 0:
        raise EvidenceError("Empty artifacts are not evidence.")
    return {"path": str(path), "sha256": digest.hexdigest(), "bytes": size}


def state_path(value):
    path = Path(value).absolute()
    return path.parent.resolve() / path.name


@contextmanager
def locked(path):
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise EvidenceError("State is locked. Investigate the writer; never automatically remove its lock.") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(f"pid={os.getpid()}\n")
        yield
    finally:
        lock.unlink()


def read_state(path):
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_STATE_BYTES:
            raise EvidenceError("State must be a regular file no larger than 5 MiB.")
        flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_NONBLOCK", 0))
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_STATE_BYTES or
                    (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)):
                raise EvidenceError("State changed while being opened.")
            data = stream.read(MAX_STATE_BYTES + 1)
        if len(data) > MAX_STATE_BYTES:
            raise EvidenceError("State exceeds the 5 MiB bound.")
        state = json.loads(data.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("State is missing, invalid, or inaccessible; it was not replaced.") from exc
    validate_state(state)
    return state


def validate_state(state):
    try:
        if set(state) != {"schema_version", "candidate", "created_at", "scope", "gates", "events"}:
            raise EvidenceError("State has missing or unsupported fields.")
        if type(state["schema_version"]) is not int or state["schema_version"] != SCHEMA_VERSION:
            raise EvidenceError("Unsupported state schema version.")
        candidate(state["candidate"])
        timestamp(state["created_at"])
        bounded_text(state["scope"], "Scope")
        gates = state["gates"]
        if not isinstance(gates, list) or not 1 <= len(gates) <= 50:
            raise EvidenceError("State requires 1 to 50 explicitly configured gates.")
        by_name = {}
        for gate in gates:
            if set(gate) != {"name", "level", "environment", "component", "scope"}:
                raise EvidenceError("Invalid gate fields.")
            canonical = gate_spec(f'{gate["name"]}={gate["level"]}@{gate["environment"]}/{gate["component"]}', gate["scope"])
            if canonical != gate or gate["scope"] != state["scope"] or gate["name"] in by_name:
                raise EvidenceError("Gates must be unique and use the declared scope.")
            by_name[gate["name"]] = gate
        if not isinstance(state["events"], list) or len(state["events"]) > 2000:
            raise EvidenceError("State events must be a list of at most 2000 entries.")
        previous = None
        observations = {}
        for index, event in enumerate(state["events"], 1):
            expected = {"sequence", "gate", "status", "level", "candidate", "scope", "environment", "component",
                        "observed_at", "recorded_at", "deployment_id", "note", "artifacts"}
            if set(event) != expected or type(event["sequence"]) is not int or event["sequence"] != index:
                raise EvidenceError("Invalid or nonsequential event fields.")
            gate = by_name[event["gate"]]
            if any(event[key] != gate[key] for key in ("level", "scope", "environment", "component")):
                raise EvidenceError("Event does not match its configured gate.")
            if event["candidate"] != state["candidate"] or event["status"] not in STATUSES:
                raise EvidenceError("Event candidate or status is invalid.")
            observed, recorded = timestamp(event["observed_at"]), timestamp(event["recorded_at"])
            if observed > recorded + timedelta(seconds=60) or (previous and recorded < previous):
                raise EvidenceError("Event timestamps are inconsistent.")
            prior = observations.get(event["gate"])
            if prior and (observed < prior[0] or (
                    observed == prior[0] and event["status"] == "passed" and prior[1] != "passed")):
                raise EvidenceError("Gate observations cannot go backward; clearing uncertainty needs a strictly later observation.")
            observations[event["gate"]] = (observed, event["status"])
            previous = recorded
            bounded_text(event["note"], "Note")
            if event["level"] == "local":
                if event["deployment_id"] is not None:
                    raise EvidenceError("Local evidence must not claim a deployment identity.")
            else:
                bounded_text(event["deployment_id"], "Deployment identity", 500)
            artifacts = event["artifacts"]
            if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= 20:
                raise EvidenceError("Each event requires 1 to 20 artifact receipts.")
            seen = set()
            for artifact in artifacts:
                if set(artifact) != {"path", "sha256", "bytes"}:
                    raise EvidenceError("Invalid artifact receipt fields.")
                relative_artifact(artifact["path"])
                if artifact["path"] in seen:
                    raise EvidenceError("Duplicate artifact receipt.")
                seen.add(artifact["path"])
                if not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
                    raise EvidenceError("Invalid artifact digest.")
                if type(artifact["bytes"]) is not int or not 1 <= artifact["bytes"] <= MAX_ARTIFACT_BYTES:
                    raise EvidenceError("Invalid artifact byte count.")
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise EvidenceError("Invalid state structure; it was not replaced.") from exc


def write_state(path, state, create=False):
    validate_state(state)
    data = (json.dumps(state, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    if len(data) > MAX_STATE_BYTES:
        raise EvidenceError("State exceeds the 5 MiB bound; start a new candidate checkpoint.")
    descriptor, temporary = tempfile.mkstemp(prefix=".delivery-state-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if create:
            # A hard link publishes the complete temporary file atomically and
            # refuses a state created by a non-cooperating writer during init.
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize(args):
    path = state_path(args.state)
    candidate(args.candidate)
    scope = bounded_text(args.scope, "Scope")
    gates = [gate_spec(value, scope) for value in args.gate]
    state = {"schema_version": SCHEMA_VERSION, "candidate": args.candidate,
             "created_at": iso(now_utc()), "scope": scope, "gates": gates, "events": []}
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked(path):
        if path.exists() or path.is_symlink():
            raise EvidenceError("State already exists; use a new path for a new candidate.")
        write_state(path, state, create=True)
    return {"result": "initialized", "candidate": args.candidate, "notice": DISCLAIMER}, 0


def record(args):
    path = state_path(args.state)
    with locked(path):
        state = read_state(path)
        if candidate(args.candidate) != state["candidate"]:
            raise EvidenceError("Candidate differs from checkpoint; create a new checkpoint for new source.")
        gate = next((item for item in state["gates"] if item["name"] == args.gate), None)
        if gate is None:
            raise EvidenceError("Gate is not configured in this checkpoint.")
        if any(getattr(args, key) != gate[key] for key in ("level", "environment", "scope", "component")):
            raise EvidenceError("Level, environment, component, and scope must exactly match the configured gate.")
        observed, current = timestamp(args.observed_at), now_utc()
        if observed > current + timedelta(seconds=60):
            raise EvidenceError("Observation cannot be more than 60 seconds in the future.")
        artifacts = [artifact_receipt(path.parent, value, (path, path.with_name(path.name + ".lock")))
                     for value in args.artifact]
        event = {"sequence": len(state["events"]) + 1, "gate": args.gate, "status": args.status,
                 "candidate": args.candidate, "level": args.level, "scope": args.scope,
                 "environment": args.environment, "observed_at": iso(observed),
                 "component": args.component,
                 "recorded_at": iso(current), "deployment_id": args.deployment_id,
                 "note": args.note, "artifacts": artifacts}
        state["events"].append(event)
        write_state(path, state)
    return {"result": "recorded declaration", "sequence": event["sequence"],
            "status": args.status, "notice": DISCLAIMER}, 0


def check(args):
    if not math.isfinite(args.max_age_hours) or args.max_age_hours <= 0:
        raise EvidenceError("Maximum age must be a finite positive number of hours.")
    path = state_path(args.state)
    with locked(path):
        state = read_state(path)
        issues = []
        if candidate(args.candidate) != state["candidate"]:
            issues.append("Expected candidate differs from checkpoint.")
        current = now_utc()
        if timestamp(state["created_at"]) > current + timedelta(seconds=60):
            issues.append("Checkpoint creation timestamp is in the future.")
        latest = {event["gate"]: event for event in state["events"]}
        deployments = {}
        for gate in state["gates"]:
            event = latest.get(gate["name"])
            prefix = gate["name"] + ": "
            if event is None:
                issues.append(prefix + "no recorded evidence.")
                continue
            if event["status"] != "passed":
                issues.append(prefix + "latest declaration is " + event["status"] + ".")
            age = current - timestamp(event["observed_at"])
            if age.total_seconds() < -60 or age.total_seconds() > args.max_age_hours * 3600:
                issues.append(prefix + "observation is stale or in the future.")
            if timestamp(event["recorded_at"]) > current + timedelta(seconds=60):
                issues.append(prefix + "recording timestamp is in the future.")
            for artifact in event["artifacts"]:
                try:
                    actual = artifact_receipt(path.parent, artifact["path"],
                                              (path, path.with_name(path.name + ".lock")))
                    if actual != artifact:
                        issues.append(prefix + "artifact bytes differ from the recorded receipt.")
                except EvidenceError as exc:
                    issues.append(prefix + str(exc))
            if event["level"] != "local":
                deployments.setdefault((event["environment"], event["component"]), set()).add(event["deployment_id"])
        if any(len(identities) > 1 for identities in deployments.values()):
            issues.append("Deployed/live declarations disagree on deployment identity for a component in an environment.")
    return {"result": "needs attention" if issues else "recorded gates consistent",
            "candidate": state["candidate"], "issues": issues, "notice": DISCLAIMER}, 1 if issues else 0


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a private checkpoint for one full commit and scope.")
    init.add_argument("--state", default=".delivery/state.json")
    init.add_argument("--candidate", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--gate", action="append", required=True, metavar="NAME=LEVEL@ENVIRONMENT[/COMPONENT]")
    init.set_defaults(action=initialize)
    add = commands.add_parser("record", help="Append a declaration with nonempty local artifact receipts.")
    add.add_argument("--state", default=".delivery/state.json")
    add.add_argument("--candidate", required=True)
    add.add_argument("--gate", required=True)
    add.add_argument("--level", choices=LEVELS, required=True)
    add.add_argument("--status", choices=STATUSES, required=True)
    add.add_argument("--scope", required=True)
    add.add_argument("--environment", required=True)
    add.add_argument("--component", default="default", help="Exact configured component; default when omitted in the gate.")
    add.add_argument("--observed-at", required=True, help="Actual observation time, ISO 8601 UTC ending in Z.")
    add.add_argument("--deployment-id", help="Actual immutable deployed image/release identity for deployed/live claims.")
    add.add_argument("--artifact", action="append", required=True, help="Path relative to the state directory; no symlinks.")
    add.add_argument("--note", required=True, help="Scope and limitations; never include secrets or personal data.")
    add.set_defaults(action=record)
    verify = commands.add_parser("check", help="Check declared gates and bytes, without granting release approval.")
    verify.add_argument("--state", default=".delivery/state.json")
    verify.add_argument("--candidate", required=True)
    verify.add_argument("--max-age-hours", type=float, default=24)
    verify.set_defaults(action=check)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result, code = args.action(args)
    except (EvidenceError, OSError) as exc:
        # No artifact contents, URLs, notes, or state payloads are emitted on errors.
        result = {"result": "needs attention", "error": str(exc) if isinstance(exc, EvidenceError)
                  else "Filesystem operation failed; existing evidence was not intentionally replaced.",
                  "notice": DISCLAIMER}
        code = 2
    print(json.dumps(result, ensure_ascii=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
