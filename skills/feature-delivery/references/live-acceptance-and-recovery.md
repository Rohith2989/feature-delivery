# Live acceptance, bounded effects and recovery

Read this for authorized testing against a deployed application, paid providers, asynchronous operations, or a live flow that may partially fail.

## Test the customer's actual path

Confirm the target environment and designated test identity. Exercise ordinary customer permissions for customer features; an administrator's success does not prove that a customer can use them. Record relevant roles, plan limits and workspace settings without copying credentials. Do not silently create another account or reset quotas to get a passing result.

Choose a small set of representative scenarios based on the behavior changed: a normal successful flow, an honest empty or partial result, an appropriate permission or limit refusal, and an interruption or provider error when it matters. Use real authorized records and suppliers for claims of live integration. Label seeded fixtures, mocks, historic artifacts and local checks explicitly.

For async features, observe acceptance of the request, the persisted operation, progress and final output. Reload or reconnect to the same operation when continuity is part of the feature. If a report or export is promised, obtain it from the actual tested flow and check that its identity, contents, filters and coverage match the request. A screenshot of a button does not establish successful export.

Keep UI progress truthful. Derive stages and counts from durable work where possible; use an indeterminate state when the amount is unknown. Do not animate an invented percentage to 100% while work is incomplete. Show waiting, retrying, partial, cancelled and failed states as distinct outcomes, with an actionable next step. Customer-facing status should describe useful work without exposing infrastructure internals, credentials or raw provider logs.

Visual inspection matters for changed interfaces and generated artifacts. Check the affected layout at supported widths, long or empty content, overlays, focus and scroll behavior as relevant. For multipage documents, inspect the pages whose layout or generated content may differ; for a new report template, inspecting every generated page may be necessary. Produce a PDF evidence pack only when requested or useful to the delivery requirement.

## Bound spending and side effects before the first call

Where actions incur money or durable external effects, identify the applicable limit and how the server enforces it across concurrent requests and retries. Track the appropriate units: currency, tokens, requests, rows or supplier credits. A UI estimate alone cannot enforce a server budget.

Reserve enough for a call's conservative maximum when possible, then reconcile to actual cost. Include retries, retrieval, embedding and other billable steps when they count against the authorized cap. If the operation cannot fit within the cap, refuse or deliver an explicitly permitted partial result. Do not silently raise limits, change an agreed model/provider or bypass accounting to obtain a success. Routine choices within the user's existing authority remain yours to make.

Before starting a paid or externally mutating acceptance run, record a small operation envelope:

- The exact account, target and requested result.
- The allowed cost or effect, request count and time bound.
- The operation or idempotency key and how to look up the result.
- The events that stop further calls and who can resolve an unknown outcome.

Use existing server controls rather than inventing client-only enforcement. The envelope should be proportionate: a read-only page check does not need a billing ledger, while a paid job with retries does.

## Retry only after reconciling the previous attempt

Distinguish a confirmed refusal, a confirmed effect and an unknown outcome. A timeout after sending a request may mean the provider accepted it. Look up the existing operation, provider receipt or idempotency result before submitting again. Never infer "nothing happened" from missing client output.

Retry transient failures only within the original authorization, budget and deadline, using the same idempotency identity where the service supports it. Do not retry invalid credentials, permanent validation failures or policy refusals until their cause changes. Repeatedly clicking a paid action is not a test strategy.

Cancellation may stop local waiting without cancelling remote work. Verify the provider or worker state before releasing a reservation or declaring cancellation complete. Preserve unresolved holds and unknown effects until reconciled through the documented process; do not erase them to restore quota. Keep external compensating actions explicit because deleting a local row does not undo a provider charge or published message.

## Stop cleanly when evidence is insufficient

Stop additional effects when a hard limit is reached, current readiness fails, identity is wrong, the target differs from authorization, data integrity is uncertain, or an operation's external outcome remains unknown. Continue safe diagnosis and evidence collection. Ask only for the missing decision or access required to proceed.

An empty dataset, unavailable supplier or insufficient evidence can be an honest product outcome. Verify that recovery, explanations and retained state work without manufacturing content or claiming a full report. A blocked live case stays open even if local tests pass.

After a real defect, preserve the failing case and operation identity, implement a focused correction, complete the checks appropriate to that correction, deploy through the authorized path, and repeat the affected live flow within the remaining bounds. Avoid re-running unrelated paid scenarios after every edit.

## Leave the next engineer a usable state

Record the candidate and running release, account scope, operation IDs, actual outputs, cost or quota state, unresolved effects, recovery action and next safe step. Keep credentials in their authorized secret store and provide retrieval instructions instead of copying them into a public handoff.

Completion reporting should make four things easy to distinguish: implemented behavior, checks actually performed, behavior observed live, and remaining limitations. Link durable receipts where the audience has access. A plausible explanation, past screenshot or other agent's confidence is not a substitute for the current result.
