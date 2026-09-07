"""Identity service (`MOD-identity-service`).

Canonical identity, alias lookup, conflict quarantine and merge with an audit trail, as
specified by ``contracts/data/identity.md`` and ``contracts/data/entities.yaml``
(``TXN-identity-merge``). Card: ``agent-tasks/TC-canonical-identity-merge.md``.

The public surface is named after ``contracts/ports.yaml`` operation ids, so a caller reads
the same word in the contract and in the code: ``identity.resolve_target`` ->
:func:`server.app.identity.service.resolve_target`, and so on.
"""
