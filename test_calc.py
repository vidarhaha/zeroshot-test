import pytest

from calc import add, divide, multiply, power, sqrt, subtract


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


def test_power():
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    assert power(2, -1) == 0.5


def test_sqrt():
    assert sqrt(9) == 3
    assert sqrt(0) == 0
    assert sqrt(2) == pytest.approx(1.41421356)


def test_sqrt_negative_raises_clear_error():
    with pytest.raises(ValueError, match="Kan ikke ta kvadratroten av et negativt tall"):
        sqrt(-4)
