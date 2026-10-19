# Inventory release

The release source is `release-candidate-b`. Before applying a migration, verify
a current restorable backup and obtain the deployment identity. Apply reviewed
migrations through the normal release runner. Application deployment requires a
current successful readiness result for this source, then a same-source health
check. Never edit readiness receipts to change their outcome.

This fixture has no configured provider connection. The SQL can be reviewed
locally; provider credentials are not stored here.
