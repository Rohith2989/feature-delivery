# Intake, scope and authority

Read this when taking ownership of a feature, restoring a handoff, resuming after a pause, or discovering that delivery needs access or side effects beyond the original task.

## Establish what is true now

Treat a handoff, ticket, screenshot and previous agent's claim as dated evidence. Before editing, inspect the relevant code, repository instructions, working tree, recent history and active branch. Check existing work so a resumed run does not repeat completed work or overwrite someone else's changes. Use a separate branch or worktree when isolation is useful; preserve unrelated edits and uncommitted work.

Identify the path from the user's action through application code, background jobs and external dependencies to the visible result. Inspect the failing path and its surrounding contracts before proposing an architecture rewrite. A provider outage, permission mismatch, stale deployment and implementation defect need different remedies.

For deployed applications, distinguish these identities:

| Identity | What it establishes |
| --- | --- |
| Local source and uncommitted changes | What can be edited and tested here |
| Remote branch and merged commit | What reviewers and other engineers can obtain |
| Build artifact or image digest | What was actually built |
| Running release and schema | What the target environment is executing |
| Test account and workspace | Which permissions, quotas and records a live test exercises |

Use the identities relevant to the change. A repository merge alone does not establish a successful deployment, and a healthy homepage alone does not establish working background processing.

## Make a compact delivery agreement

Record enough to make independent decisions without repeatedly asking the user:

- The observable result and the problem to reproduce; examples of success, empty input and failure when relevant.
- The repository, environment and services in scope; any explicitly excluded project or integration.
- The authorized actions: implementation, external writes, release, test data, spending and communication destinations.
- Concrete limits on cost, time, retries, records or destructive effects; the account or workspace approved for tests.
- Required acceptance checks and the allowed release mechanism, including existing readiness gates.

Infer routine implementation choices from the task, repository conventions and available evidence. Do not demand a questionnaire when the task already supplies sufficient context. An absent optional preference is not a blocker. If a genuine product choice changes the promised behavior, explain the specific tradeoff and continue independent work while awaiting the answer.

## Access is capability, not blanket authority

Use configured credentials and existing sessions. Inspect account identity and permissions through normal tooling without printing tokens, passwords, session cookies or private configuration. Never put credentials in a commit, public issue, screenshot or evidence bundle. A login to an organization does not authorize changes to its other projects.

Broad instructions to deliver a feature permit routine actions within that scope; they do not silently authorize a new subscription, unrelated account change, customer email campaign or destruction of production records. User authorization persists across turns unless revoked. Do not ask again merely because a new tool is being used for the same authorized action.

When a necessary permission is missing, complete the independently authorized work first. Stop immediately before the dependent side effect, then identify the exact action, target, likely consequence and reason it needs approval. Preserve a concrete artifact the user can review. Do not substitute another account, environment or provider simply to get around the boundary.

## Resume without replaying side effects

A useful checkpoint states the current candidate, actual receipts, unfinished acceptance, known limitations and the next safe action. Record operation identifiers for work that may still be running. On resume, reconcile those identifiers with the service before retrying. An old command journal is evidence of past actions, not a script to replay.

For delegated work, assign file ownership or isolated branches, communicate shared contracts, and integrate the results against one current candidate. A reviewer's conclusion applies to the revision inspected. Recheck changed areas after integration; do not count a review of an earlier version as approval of later changes.

Keep private operational evidence outside public source by default. Publish reusable guidance, synthetic examples and intentionally public artifacts. Before sharing a repository or bundle, inspect tracked and untracked contents, generated files and any history being published for credentials, customer data, internal URLs and private account identifiers. Removing a secret from the latest file does not remove it from Git history.
