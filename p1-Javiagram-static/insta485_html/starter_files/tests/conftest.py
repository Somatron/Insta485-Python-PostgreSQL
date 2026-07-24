"""
Shared test fixtures for all tests.

Pytest automatically discovers the custom commandline flags in this file.
"""
import pytest


def pytest_addoption(parser):
    """Add a custom command line option to skip user authentication."""
    parser.addoption(
        "--noauth",
        action="store_true",
        default=False,
        help="Skip user login."
    )


@pytest.fixture(name="noauth")
def setup_teardown_noauth(request):
    """Return value of --noauth command line flag."""
    return request.config.getoption('--noauth')
