# Validation and release

Read this when selecting checks, preparing a release, changing persistent data, or establishing that the reviewed and tested candidate is the one being deployed.

## Select checks by the failure being prevented

First reproduce the reported behavior or capture the strongest available evidence when reproduction is unsafe or unavailable. Record the input, identity, environment and observable result. If reproduction fails, distinguish an intermittent issue from a disproved hypothesis; do not manufacture a failing test merely to justify a change.

Use the cheapest checks that meaningfully reduce the change's risk. Follow repository requirements and add coverage for the actual failure and important neighboring behavior. Examples:

| Change | Useful evidence |
| --- | --- |
| Reversible copy or styling adjustment | Inspect the affected view at relevant sizes and states |
| Permission, quota or billing decision | Allowed and denied identities, boundary values, durable accounting and duplicate requests |
| Async or external-provider workflow | Start, progress, completion, timeout, cancellation and an interrupted or duplicate request where relevant |
| Migration or storage contract | Compatible reads/writes, transition state, data preservation and recovery strategy |
| Report or export | A real generated artifact; check content, filters, readability and the affected pages or views |

Do not require every row for every change. Avoid tests that merely repeat the implementation or assert that a heading exists. For a live-first task, use live acceptance as authorized; perform required pre-release safety checks and explain any material limit. Do not duplicate entire acceptance suites across environments without a reason.

Inspect failures before widening or repeating a suite. Separate a product regression from a flaky fixture, missing tool or infrastructure outage. A skipped test or failed check remains an explicit limit, even when an unrelated check passes. Re-run relevant checks after subsequent code changes.

## Keep the candidate identifiable

Use meaningful commits organized around reviewable behavior or dependencies. Keep commit and PR counts out of the success criteria. Authenticate as the authorized repository user; respect configured authorship and do not invent another person's identity.

Record the source revision, relevant uncommitted state, test result and build identity. For container or packaged releases, prefer an immutable digest or checksum when available. If building from a dirty tree, make that fact explicit and retain a way to reproduce the input; a source SHA alone does not describe it.

Independent review is valuable for security boundaries, money, concurrency, persistent data, broad architecture changes and other difficult-to-reverse behavior. Give the reviewer the actual diff and context, resolve material findings, and bind the review to the revision inspected. Do not force a paid review service or ceremonial extra reviewer for a low-impact edit.

## Honor the project's release path

Inspect the existing release documentation and current repository settings. Use required checks and the authorized release mechanism. A manual workflow, local release command and automatic CI have different costs and permissions. Do not enable paid automation, disable required checks, change branch protection or bypass a blocked gate merely to make the release succeed. If the user has authorized manual releases or disabled optional automation, preserve that choice.

Before a release, confirm the actual environment, service, credentials and artifact. Readiness should reflect the current candidate and current dependencies: schema compatibility, required configuration, worker capability and service health as applicable. An old green receipt is not a substitute for a failed current gate. Investigate and repair the blocked condition within scope, or report the exact blocker.

## Treat persistent changes as a separate risk

Prefer compatible, additive transitions when old and new application versions may overlap. Consider long-running jobs, rollbacks and readers that still expect the old shape. Document when a later cleanup is safe rather than dropping compatibility immediately.

For a risky or irreversible migration, verify a recovery route before applying it. Check that an authorized backup or recovery point covers the correct database and relevant time, that the team has restoration access, and that its retention and restoration procedure are usable. A dashboard label saying "backup exists" is not proof that it can restore this change. Use a recent isolated restore exercise or another proportionate validation where feasible; explicitly state when restoration has not been exercised. Do not restore production as a casual test.

Choose recovery based on the failure: revert an application artifact, roll forward with a compatible fix, disable a feature, or restore data through an approved procedure. A previous application image may be incompatible with a changed schema. Do not automatically run a destructive down migration or erase valid new records to force a rollback.

## Establish the deployed result

After release, match the running artifact and schema to the intended candidate using supported deployment metadata. Verify relevant web and worker processes, then perform the authorized user flow from the live-acceptance reference. Preserve the actual operation IDs and outputs. Report source merged, deployment complete and live behavior verified as separate facts.

If merge or deployment permission is absent, leave the complete, reviewed candidate and exact next command or workflow ready. Call the work ready for release rather than live. A tool error is not a successful release, and an unobserved background job is not a completed feature.
