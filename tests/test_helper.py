import pytest
from terminalcast.helper import format_bytes

@pytest.mark.parametrize("size, expected", [
    (1023, "1023 B"),
    (1024, "1.0 KB"),
    (1536, "1.5 KB"),
    (1024 * 1024 * 5, "5.0 MB"),
    (1024 * 1024 * 1024 * 2.3, "2.3 GB"),
    (None, "-"),
    ("", "-"),
    ("abc", "-"),
])
def test_format_bytes(size, expected):
    assert format_bytes(size) == expected
