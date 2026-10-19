# Optional recorded-evidence checks

`scripts/delivery_state.py` is a Python 3.10+ standard-library helper for keeping
private, candidate-bound evidence. The skill works without it. It does not execute
tests, contact services, deploy code, authenticate a claim, or grant approval.
Its successful check means only that recorded declarations and retained artifact
bytes satisfy the configured consistency checks.

Run `python path/to/scripts/delivery_state.py --help` for the supported commands.
Use a new state file for a different candidate or scope. Keep state and evidence in
an ignored private folder, never in this public skill repository.

For example, from the project root (replace the candidate with a full real SHA):

```bash
python /path/to/feature-delivery/scripts/delivery_state.py init \
  --state .delivery/state.json --candidate FULL_SOURCE_SHA \
  --scope 'CSV export preserves Unicode and quoted values' \
  --gate 'regression=local@developer'
```

A deployed application may additionally configure `release=deployed@staging` and
`customer-flow=live@staging`; a local library need not configure deployment gates.
Gate level and environment must match exactly: a browser check cannot replace
unit tests just by having a supposedly higher evidence level.

For multiple independently released components in one environment, configure the
optional component explicitly, for example `api-release=deployed@staging/api`,
`api-smoke=live@staging/api`, and equivalent `/worker` gates. Record each with
`--component api` or `--component worker` and its own real deployment identity.
The default component is `default`. Identity agreement is checked per environment
and component, not between unrelated services.

After actually running a check, retain its redacted output beneath the state
directory and record it. Example syntax (use real observation time and evidence):

```bash
python /path/to/feature-delivery/scripts/delivery_state.py record \
  --state .delivery/state.json --candidate FULL_SOURCE_SHA \
  --gate regression --level local --environment developer \
  --status passed --scope 'CSV export preserves Unicode and quoted values' \
  --observed-at 2030-04-12T10:01:00Z \
  --artifact evidence/regression.txt --note 'Actual test command and assertions'

python /path/to/feature-delivery/scripts/delivery_state.py check \
  --state .delivery/state.json --candidate FULL_SOURCE_SHA --max-age-hours 24
```

The date above is illustrative, not a receipt. A real record needs the real time.
Use the actual full source identity, not the literal `FULL_SOURCE_SHA` placeholder.
For deployed/live records, supply the real `--deployment-id` as well. Never record
a pass before performing its assertion. Preserve failed, partial and unknown events;
the helper must not fall back to an older pass when the latest result is uncertain.
Observations for each gate cannot go backward. A pass at the same observation
instant cannot clear failure, partial coverage or an unknown result; retain the
uncertainty until a strictly later real observation supports the pass. Fractional
seconds are preserved. Re-recording an old receipt does not make it fresh.

Artifact paths are relative to the state file's directory. The helper checks
retained bytes, candidate/scope/environment, record age and configured gates. It
does not establish that a provider settled, a schema is current, a person approved
a release, a browser had the right role, or a screenshot depicts a real service.
Read the actual output and external state before making those claims. Freshness
requirements remain task-specific; a default age does not extend any authority.

Writes use a lock and atomic replacement. A busy or stale lock is a reason to
reconcile the owner, not delete it automatically. Protect the private directory
from untrusted concurrent writers. Do not add credential files or sensitive raw
logs as evidence; ignore rules are not a secret scanner or encryption.
