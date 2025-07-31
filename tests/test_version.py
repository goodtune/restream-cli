from restream_io.cli import get_version

def test_version_fallback():
    # This test assumes no installed distribution; fallback should return something non-empty
    v = get_version()
    assert v, "Version should not be empty"
