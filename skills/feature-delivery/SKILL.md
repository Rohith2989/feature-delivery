---
name: feature-delivery
description: Own a requested software feature or fix from investigation through implementation, relevant tests, authorized release, and verification of real user workflows. Use for end-to-end delivery or resuming unfinished delivery; not for advice-only requests or an unrelated production audit.
---

# Feature Delivery

Take responsibility for the requested outcome. Continue through implementation,
verification, authorized release, and fixing regressions discovered in acceptance.
The measure is a working feature with evidence appropriate to its risk. Commit
counts, PR counts, elapsed hours, screenshots alone, and a green status badge are
not substitutes for that outcome.

Autonomy operates within the user's scope, existing authorization, tool permissions,
and project release rules. This skill supplies no additional access or authority.
Make routine implementation decisions; do not keep asking permission already given.

## Establish the actual starting point

Read the user's current request and applicable repository instructions. Inspect
the working tree, recent history, relevant code, tests, and existing delivery work.
Preserve unrelated changes. Use an isolated branch/worktree when that prevents
collisions; do not reset, stash, discard, or merge someone else's work by default.
Validate generated workspace paths before writing. Require preparation commands to
succeed before dependent mutations; a failed directory creation must not become an
empty path, the filesystem root, or an unrelated checkout used as a fallback.

Identify the user-visible behavior, affected surfaces, failure reproduction, and
acceptance criteria. For a new feature, establish the existing behavior and an
observable example of the desired result. Trace the real path through UI/API,
ownership, queue/worker, storage, external dependencies, and deployment only as far
as relevant. Diagnose causes before broad rewrites. Treat old handoffs as dated
claims; reconcile them with actual source, releases, schema, and current work.

Infer setup from available configuration and authorized sessions. Record only
what matters: target environment, ordinary test identity/data boundary, required
checks, deployment path, migration/recovery needs, budget/deadline, and external
actions already authorized. Never request secrets in chat or copy auth state into
evidence. Read [intake and authority](references/intake-and-authority.md) when access,
ownership, deployment scope, or production side effects need clarification.

Keep a short working checklist. A small change needs a small process; a migration,
paid integration, or multi-service change needs stronger evidence. Do useful
independent work before raising a genuine product/access blocker. Ask a targeted
question only where its answer is necessary; prepare a concrete reviewable result
before a required approval. Do not treat elapsed time or a missing reply as approval.

## Implement a coherent change

Choose the smallest design that fixes the cause and fits the existing system.
Preserve API/data compatibility or provide an explicit migration. Handle relevant
empty, partial, delayed, denied, canceled, and failed outcomes as product behavior.
Keep customer progress truthful: observed stages and useful recovery, not invented
percentages or raw infrastructure logs. Do not turn uncertainty into success.

Use meaningful commits with the configured authorized attribution. Split changes
when it helps review, rollback, or deployment order; never manufacture commit/PR
volume. Keep scope and ownership clear if delegating. Parallelize independent
investigation or review where useful; coordinate edits and integrate conclusions.
The primary agent still owns the complete result.

## Verify, release, and verify again

1. Show that a relevant reproduction or acceptance example distinguishes the old
   behavior from the intended one. Add regression coverage when meaningful.
2. Run the checks justified by changed behavior and repository requirements. Include
   real boundaries where mocks cannot establish correctness: persistence,
   permissions, queues, transport, concurrency, or UI interaction as applicable.
3. Review the resulting diff and integration. Use independent review for complex or
   risky changes when available. Resolve material findings. A canceled, unavailable,
   skipped, or failed required check is not a pass. Use an authorized equivalent
   only when project policy allows it; never silently bypass a required gate.
4. Bind release evidence to the exact candidate and artifact. Follow the project's
   real migration, active-work, readiness, and rollout sequence. A built image is
   not a published image; a merged PR is not a running release. Read
   [validation and release](references/validation-and-release.md) for release,
   migration, rollback, and artifact identity details.
5. When release is in scope and authorized, release the verified candidate and
   check the running version and actual readiness. If live access or authorization
   is missing, finish the independently verifiable work and report the narrow
   remaining blocker. Do not substitute staging for production without disclosure.
6. Exercise the actual user workflow in the target environment. Use a normal
   authorized role for customer permissions/quotas, not privileged bypass. Test the
   relevant adverse/recovery cases within the approved data, spend, and retry bounds.
   For a library/CLI/local tool, the real workflow may be installation and execution
   in a clean consumer environment; do not invent a production deployment requirement.
7. Fix issues found, repeat the affected checks, and release/retest the changed
   candidate as required. Do not repeat unrelated paid runs or entire test matrices
   after their exact evidence is still valid. Read
   [live acceptance and recovery](references/live-acceptance-and-recovery.md) for
   identity, evidence, unknown effects, and bounded retries.

Stop the affected release or paid action when readiness fails, authorization or
funding expires, the approved budget/deadline is reached, a material regression is
observed, or a side effect is unknown. Reconcile the original operation instead of
creating a new identity, account, quota, or retry to escape the stop. Continue safe
diagnosis and independent work; state the concrete blocker and next permitted step.

## Preserve progress and report the outcome

Maintain enough private evidence that another agent can continue without repeating
completed work: exact source/artifact/release identifiers, commands and outcomes,
environment and role, observed assertions, original operation IDs for recovery,
remaining findings, and next safe action. Keep historical evidence immutable; append
corrections rather than rewriting failures as passes. Revalidate claims whose source,
scope, environment, role, or time window no longer matches. Do not automatically
schedule continuations or send external messages without user authorization.

Use [delivery and handoff templates](references/delivery-templates.md) when a durable
brief, acceptance matrix, checkpoint, or final report would help. Templates are
optional, not paperwork required for every edit. The optional
[evidence helper](references/evidence-helper.md) can check recorded gate consistency
and artifact hashes; it cannot prove live behavior or authorize a release.

Tell the user what changed, what was actually tested, the observed result, and any
material limit. Distinguish **implemented**, **locally verified**, **merged**,
**deployed**, **verified in the target environment**, and **still pending**. Declare
delivery complete only when the requested scope's applicable acceptance is met;
otherwise report the precise partial result. Include links to reviewable changes
and appropriately redacted evidence. Never mark a ticket Done or advertise live
success based only on code, mocks, a submission acknowledgment, or a generated receipt.
