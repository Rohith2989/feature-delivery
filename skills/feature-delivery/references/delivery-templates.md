# Optional delivery templates

Use the smallest subset that makes the task clear. Keep filled copies private in
the project's approved evidence location (for example, ignored `.delivery/`). These
are prompts for reasoning, not an authorization form or proof of execution.

## Task brief

```text
Outcome and a concrete user example:
Existing behavior / reproduction:
In scope / explicitly deferred:
Repository and relevant instructions:
Current branch, source, pending work and owner:
Target environment and real user role:
Existing authorized actions and their boundaries:
Test data, spend/retry/deadline limits:
Required review/release/readiness gates:
Acceptance cases and observable assertions:
Migration, recovery or rollback considerations:
Genuine missing decision/access (if any):
```

Infer what the existing request and repository already establish. Do not hand this
entire form to the user as a mandatory questionnaire.

## Acceptance matrix

| Behavior / risk | Setup and role | Action | Observable assertion | Evidence and exact version | Result / limit |
| --- | --- | --- | --- | --- | --- |
| Primary workflow | Authorized ordinary user and controlled data | Perform the actual operation | Persisted result matches the requested behavior | Actual test/run ID, source/artifact, environment, timestamp | Pass, partial, fail, unknown or pending |
| Relevant recovery | Same logical operation after interruption | Reconnect/reload or documented recovery | No duplicate side effect; result or truthful unresolved state | Original operation ID and bounded observation | Never turn unknown into zero or success |

Replace the example rows with the relevant scenarios. Permission checks, screen
sizes, empty data, payments, migrations, concurrency, offline behavior, etc. belong
only where the change makes them material.

## Evidence entry

```text
Claim and scope:
Observation time and validity boundary:
Source commit / artifact identity:
Target environment and effective role (no session or credentials):
Exact command or user actions:
Expected assertion / observed result:
Exit code and real external run/release/operation ID, when applicable:
Evidence location and hash, if retaining a file:
Known uncertainty / mock or seeded fixture limits:
```

An output file hash proves which bytes were retained, not that the claimed action
happened. A screenshot can support a UI assertion, not hidden billing or persistence.

## Checkpoint for resuming or transferring work

```text
Latest user intent and active scope:
Current timestamp and original authority/budget/deadline:
Repositories/worktrees and current source/artifact/release/schema:
Completed work with exact evidence pointers and validity:
Uncommitted work, branches/PRs and their owners:
Actual active/unknown operations, original IDs and accounting holds:
Current readiness/access/quota observations and their time limits:
Unclosed bugs, disabled features and explicit deferrals:
Schedules/automations created, destinations and retirement status:
Next safe action and conditions that must first be rechecked:
Never replay / never change:
Private access must be reestablished through normal authorized sessions:
```

Do not export cookies, refresh sessions, passwords, service keys, private customer
data or raw environment files. A recipient's access to a repository does not mean
they have the old machine's runtime, image store, credentials or authority window.

## Final delivery note

```text
Changed: [user-visible result and why].
Verified: [actual checks, environment/role, source/release, result].
Released: [merged/deployed identifiers, only if those events happened].
Limits: [pending scope, unresolved failure, or unverified environment].
Evidence: [reviewable changes and redacted proof].
```

Write the note in natural language; do not repeat empty fields. Send it to external
channels or update tickets only when that destination/action is authorized.
