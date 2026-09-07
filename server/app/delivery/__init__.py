"""Delivery service (``MOD-delivery-service``).

The digest lifecycle, kept strictly separate from the run lifecycle (``I09``): an outbox
intent committed inside the publish transaction, an attempt row committed **before** the
network call, ``unknown`` as a quasi-terminal state that only the owner leaves, and a
per-part receipt for a multi-part digest.

Contracts: ``contracts/state/delivery.yaml`` (``T-DL-00``..``T-DL-09``, ``DP-01``..``DP-05``),
``contracts/telegram/delivery.md`` 0.2.1, ``contracts/ports.yaml`` ``delivery.*``.
Card: ``agent-tasks/TC-telegram-unknown-delivery.md``.

The public surface is named after ``contracts/ports.yaml`` operation ids, so a caller reads
the same word in the contract and in the code: ``delivery.dispatch_next`` ->
:func:`server.app.delivery.service.dispatch_next`, and so on.

Plain text only, on purpose
---------------------------
``contracts/telegram/delivery.md`` §3.4 leaves three facts at ``KC``/``BLOCKED_DEPENDENCY``
-- ``callback_data`` length, the parse-mode escape table, and buttons per row. Nothing in
this package therefore sets ``parse_mode``, builds an inline keyboard or mints a
``callback_data``: §3.3's safe branch ("send plain text") is the only implementable one, and
guessing any of the three numbers is forbidden by §9 row 12.
"""
