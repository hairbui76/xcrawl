"""Secret service (``MOD-secret-service``).

The only module that reads a secret value (``contracts/ops/secrets.md`` §4.2). Three
operations, named after ``contracts/ports.yaml``:

``secret.store_provider_key``      -> :func:`server.app.secret.service.store_provider_key`
``secret.issue_task_credential``   -> :func:`server.app.secret.service.issue_task_credential`
``secret.revoke_task_credential``  -> :func:`server.app.secret.service.revoke_task_credential`

Three entities: ``secret_ref`` (pointer + state, never a value), ``task_credential`` (one
provider, one task, 900 s) and ``secret_audit`` (who touched what, with the values masked).

The blast radius, stated as a bound
-----------------------------------
``ADR-0010`` §1 and ``B13``: a worker never receives the store. It receives one credential,
for the provider its own task needs, while it holds that task's lease, for
``lease_ttl_analysis`` seconds. ``ISO-05`` is the negative of that sentence, and
:func:`server.app.secret.service.issue_task_credential` asks
``server.app.analysis.service.verify_task_lease`` -- the module that owns leases -- rather
than deciding for itself.
"""
