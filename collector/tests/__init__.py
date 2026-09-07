"""Test package marker.

Makes the module name unique (`collector.tests.test_smoke`) so pytest's rootdir-relative import
does not collide with the identically named smoke modules of the other packages.
"""
