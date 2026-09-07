"""Owner authentication and the deny-by-default scheme boundary (``MOD-auth-service``).

Card: ``agent-tasks/TC-owner-auth-session.md``. Four modules, one job each:

``csrf``
    the double-submit primitives (cookie ``rr_csrf`` vs header ``X-CSRF-Token``).
``service``
    ``auth.login`` / ``auth.logout`` / ``auth.get_session`` over ``ENT-owner`` and
    ``ENT-session``, plus Argon2id password verification and the login lockout.
``middleware``
    the security schemes of ``contracts/http/openapi.yaml`` applied as FastAPI
    dependencies, and the default-deny decision every other router depends on.
``router``
    the three HTTP handlers.

Other cards import ``server.app.auth.middleware`` -- never ``service`` -- to guard their
routes. ``middleware`` is the only public surface of this package for them.
"""

from server.app.auth import csrf, middleware, router, service

__all__ = ["csrf", "middleware", "router", "service"]
