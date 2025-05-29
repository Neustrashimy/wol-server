# tests/test_validation.py

from utils.validation import normalize_mac, InvalidMACError


def test_normalize_mac_happy_path():
    assert normalize_mac("AA:BB:CC:DD:EE:FF") == "aa:bb:cc:dd:ee:ff"


def test_normalize_mac_strip_separators():
    assert normalize_mac("aabb.ccdd.eeff") == "aa:bb:cc:dd:ee:ff"


def test_normalize_mac_invalid_length():
    import pytest

    with pytest.raises(InvalidMACError):
        normalize_mac("00:11:22")


def test_normalize_mac_invalid_format():
    import pytest
    
    with pytest.raises(InvalidMACError):
        normalize_mac("aa:bb:cc:dd:ee:xx")