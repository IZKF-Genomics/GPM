import pytest

def test_addition():
    assert 2 + 2 == 4

def test_division_failure():
    with pytest.raises(BaseException) as ex:
        x = 1 / 0