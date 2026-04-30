from qkiosk.yyyymmdd import yyyymmdd, is_yyyymmdd, today


def test_yyyymmdd_to_parts():
    d = yyyymmdd(20240115)
    assert d.to_yyyy() == 2024
    assert d.to_qq() == 1
    assert d.to_int() == 20240115


def test_today_is_yyyymmdd():
    assert is_yyyymmdd(today())
