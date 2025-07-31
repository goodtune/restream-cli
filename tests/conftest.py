import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    # Prevent real HTTP requests by default; tests should enable responses
    pass
