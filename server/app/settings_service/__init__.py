"""Settings service (``MOD-settings-service``).

Three operations, named after ``contracts/ports.yaml``:

``settings.get_config``     -> :func:`server.app.settings_service.service.get_config`
``settings.update_config``  -> :func:`server.app.settings_service.service.update_config`
``settings.test_provider``  -> :func:`server.app.settings_service.service.test_provider`

Four tables: ``settings`` (created on this module's behalf by
``0013_tc_backfill_pending_ledger``, taken over here), ``provider_config``,
``provider_test_result`` and ``source_connection``.

Why the package is ``settings_service`` and not ``settings``
------------------------------------------------------------
``SG-NAME`` of the card: the Phase 0 skeleton reserves ``server/app/settings.py`` for the
environment-driven configuration module, and a package of the same name in the same parent
package collides on import -- the ``import file mismatch`` class of failure ``PROV-P0-01``
already hit once. Renaming is a CR, not a preference.

The key never comes back
------------------------
``settings.update_config`` accepts a new API key and forwards it to ``MOD-secret-service``.
This package keeps no copy, and ``settings.get_config`` answers with a reference and a
*configured / not configured* flag -- denied case ``NC-03``, ``secrets.md`` §4.2. The one
place a value exists here is the local variable that carries it into
``secret.store_provider_key``.
"""
