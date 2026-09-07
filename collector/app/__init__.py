"""Research Radar collector application package (`collector.app`).

The collector runs as a process on the Owner's personal machine (REQ-S6.4-02), drives a
real Chrome with the project's own profile (REQ-D09) through Playwright, and talks to the
server over HTTP with a bearer token. It never reaches the database and never calls
``storage.get_health`` (denied case NC-05, ``CAPABILITY_DENIED``).
"""
