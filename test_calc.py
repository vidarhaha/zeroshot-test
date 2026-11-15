import pytest

from calc import add, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2


def test_multiply():
    assert multiply(4, 3) == 12
    assert multiply(5, 0) == 0


def test_divide():
    assert divide(10, 2) == 5
    assert divide(1, 4) == 0.25


def test_divide_by_zero_raises_clear_error():
    with pytest.raises(ZeroDivisionError, match="Kan ikke dele på null"):
        divide(1, 0)
