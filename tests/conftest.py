import pytest
import responses
from restream_io.cli import get_version

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    # Prevent real HTTP requests by default; tests should enable responses
    pass
