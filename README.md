# Feature Delivery

**Give an agent an outcome. Get implementation, verification, and a clear account of what actually shipped.**

A reusable skill for engineers who want AI agents to own a feature through the
whole delivery loop: investigate, build, test, review, release within authorized
boundaries, exercise real user workflows, and fix the defects found along the way.

Created by [Rohith](https://github.com/Rohith2989). MIT licensed. The workflow is
generalized from sustained delivery work; no company source, operational receipts,
customer data or credentials are included.

## What it changes

An agent should not stop at a patch and “you can test this now.” It should carry
the requested work to its applicable acceptance criteria, or leave a precise,
reviewable blocker when access, a product decision or a required gate prevents it.

- **Outcome ownership:** follow the actual path from the user's action to the
  persisted result, including workers and integrations when they matter.
- **Evidence tied to the release:** keep local tests, merge, artifact publication,
  deployment and live verification distinct.
- **A real feedback loop:** test relevant success and failure paths, fix discovered
  bugs, release the changed candidate, and retest the affected flow.
- **Bounded autonomy:** make routine decisions without repeated permission requests;
  preserve readiness checks, original spending limits and unknown side effects.
- **Continuity:** leave another engineer or agent enough state to continue without
  overwriting work or repeating completed paid operations.

This is about feature delivery, not the number of PRs. Small changes should stay
small. A library's consumer-install check may be its real acceptance flow; a payment
or database change needs a different standard of proof.

## Start here

Install the [skill folder](skills/feature-delivery), then give the agent a task:

```text
Use $feature-delivery to add CSV export to the activity table.
Preserve the current filters and permissions. Follow this repository's checks.
You may implement, commit, and deploy to our staging environment using the
existing release process. Test the exported file through the real staging UI.
Production release needs approval. Make routine implementation decisions and
continue until the staging acceptance passes or a concrete blocker remains.
```

The agent infers available setup from the project before asking. Provide only the
missing material context: the outcome, target environment, existing authorized
access, test-data boundary, release authority and any cost/time limits. The
[project brief](examples/project-brief.md) is an optional starting point, not a
mandatory form. Use normal sign-in or a secret store; do not paste credentials.

## Install

### Codex

Ask the built-in installer:

```text
Use $skill-installer to install the feature-delivery skill from
https://github.com/Rohith2989/feature-delivery/tree/main/skills/feature-delivery
```

Alternatively, copy `skills/feature-delivery/` into your user skill directory
`~/.agents/skills/feature-delivery/`, or into a target project's
`.agents/skills/feature-delivery/`. Review an existing destination instead of
overwriting it. Mention `$feature-delivery` in a task. If discovery has not updated,
restart the agent. These locations and invocation behavior follow the
[official Codex skills documentation](https://learn.chatgpt.com/docs/build-skills).

### Other coding agents

The entrypoint is ordinary Markdown with Agent Skills metadata. For a host that
supports this format, install the same folder using its documented skill-loading
mechanism. Otherwise, ask it to read
`skills/feature-delivery/SKILL.md` and the references linked for the current task.
Do not claim that every host discovers skills or enforces permissions identically.

The root `plugin.json` also packages the skill using the
[portable plugin format](https://developers.openai.com/plugins/build/plugins).
There are no bundled connectors, background hooks or deployment credentials.
Marketplace publication and every host's installer have not been tested here.

## What is included

| File | Purpose |
| --- | --- |
| [SKILL.md](skills/feature-delivery/SKILL.md) | Compact entrypoint; load only the guidance relevant to the work |
| [Intake and authority](skills/feature-delivery/references/intake-and-authority.md) | Establish current source, ownership, access and limits |
| [Validation and release](skills/feature-delivery/references/validation-and-release.md) | Proportionate checks, exact artifacts, migrations and recovery |
| [Live acceptance and recovery](skills/feature-delivery/references/live-acceptance-and-recovery.md) | Customer-role flows, truthful progress, retries and unknown effects |
| [Delivery templates](skills/feature-delivery/references/delivery-templates.md) | Optional brief, acceptance matrix, evidence, checkpoint and final note |
| [Evidence helper](skills/feature-delivery/references/evidence-helper.md) | Optional local record consistency and artifact hash checks |
| [Behavioral evaluations](docs/evaluations/scenarios.md) | Synthetic tasks for implementation and difficult delivery decisions |
| [Validation record](docs/VALIDATION.md) | What was actually exercised, with explicit limits |

## What the engineer sets once

The skill uses your existing test runner, release process and infrastructure. It
does not require a particular cloud, ticket tracker, browser or paid review service.

1. Identify the repository, target and requested behavior.
2. Make the necessary tools/sessions available through your normal access controls.
3. Define which external actions are authorized and the relevant data/spend limits.
4. Keep the project's required checks and deployment rules discoverable.

An agent cannot verify a live workflow without a reachable service and appropriate
identity. A skill cannot grant access, override a blocked readiness check, promise
zero bugs, or keep running after its host session ends. Ongoing schedules and
external messages require their own authorization. A blocked live case remains open.

## Develop and verify this repository

The optional helper and repository checks use Python 3.10+ and its standard
library. No provider account or paid API is needed.

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_package.py
```

On Windows, use your installed `python` command. Native Windows execution is not
claimed solely from portable source. See [the validation record](docs/VALIDATION.md)
for the platforms and scenarios actually exercised. No automatic GitHub workflow
is installed; these checks can be integrated into your team's existing process.

For a new behavioral evaluation, copy a raw fixture to an isolated workspace and
give it to an agent with the skill. Keep the
[evaluation rubric](docs/evaluations/rubric.md) out of that agent's input. Evaluate
actual actions and artifacts, not whether the final answer repeats preferred words.

Contributions should improve observable delivery decisions, fix a demonstrated
failure, or add a useful small evaluation. Avoid expanding the skill into a universal
checklist or adding private operational examples. See [CONTRIBUTING.md](CONTRIBUTING.md).
