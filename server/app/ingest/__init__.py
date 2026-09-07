"""``MOD-ingest-service`` -- the ingest path of the server.

Four operations from ``contracts/ports.yaml``, implemented in :mod:`server.app.ingest.service`
and exposed over HTTP by :mod:`server.app.ingest.router`::

    ingest.submit_batch       TXN-ingest-batch      POST /v1/ingest/batches
    ingest.commit_checkpoint  TXN-checkpoint-only   POST /v1/ingest/checkpoints
    ingest.get_receipt        (read)                GET  /v1/ingest/receipts/{key}
    ingest.get_checkpoint     (read, internal)      no route -- transport is `internal`

The package owns exactly three tables -- ``post``, ``ingest_receipt``, ``checkpoint`` -- and
reaches nothing else directly; identity, storage health and assignment leasing are called
through their owning modules' ports.

This file exists so ``server.app.ingest`` is a regular package like every other
``server/app/*`` subpackage rather than an implicit namespace package that happens to import
because the repo root is on ``pythonpath`` (finding ``F-A3R1-10``). It deliberately re-exports
nothing: a caller naming ``server.app.ingest.service`` says which layer it is calling, and a
convenience re-export here would let a router-level import look like a service-level one.
"""
