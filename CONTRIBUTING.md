# Contributing

Keep the skill useful to a capable agent. Add guidance when it changes a concrete
decision or preserves an important invariant; do not restate generic engineering
advice or turn every past incident into a mandatory ceremony.

For a workflow change, add or adapt a realistic isolated evaluation and inspect
the actions and resulting artifacts. Keep the evaluator rubric separate from the
raw input. Describe failures as well as passes. An instruction-only change may need
a behavioral evaluation more than another wording assertion.

For a helper change, run meaningful tests, including the affected refusal or
recovery behavior. Use `python3 -m unittest discover -s tests -v` and
`python3 tools/check_package.py`. Python 3.10+ is supported by source; only platforms
listed in the validation record have been exercised. Add no automatic paid jobs.

Do not submit credentials, customer data, internal URLs, actual account identifiers
or operational dumps. Use synthetic fixtures. Check generated files and history,
not just the latest diff. Keep evidence files private unless deliberately prepared
for public review. Report sensitive findings privately through GitHub's private
vulnerability reporting if available; do not publish an exploit or credential in
an issue. If private reporting is unavailable, contact the maintainer through an
available private channel without including the sensitive material initially.

The workflow must preserve user scope and host permissions. Tests must never require
a real production target, a paid provider, public posting or a secret to pass.
