# A brief an engineer can give the agent

Replace the examples with your actual project. Omit anything the repository or
current request already establishes. Supply access through normal tools, never
through passwords embedded in this document.

```text
Use $feature-delivery.

Outcome: Team members can export the currently filtered activity rows as CSV.
Acceptance: Preserve Unicode, quoting, filters and existing data permissions;
the file opens in our supported spreadsheet app. Empty results have clear behavior.

Scope: This repository and its staging application. Keep unrelated work intact.
Access: Existing repository, staging browser and release-tool sessions are available.
Test boundary: Use the team's designated ordinary QA workspace and synthetic data.
Release authority: You may commit, open/update a PR and deploy to staging through
the documented workflow. Prepare production release for approval.
Limits: Do not send customer emails, buy services, change billing or reset quotas.
Checks: Follow repository instructions; add regression coverage where it matters.

Make routine choices, implement the feature, run the appropriate checks, release
within that authority, test the real staging flow, and fix/retest defects found.
Ask only for a genuine missing decision or access. Finish with what changed,
what was actually verified, the release identity and any remaining limits.
```

For a local CLI, replace the staging instructions with clean installation and
execution against realistic inputs. For production delivery, name the target,
authorized deployment path, controlled test data and meaningful limits explicitly.
