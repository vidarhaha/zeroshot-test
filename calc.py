"""Enkel kalkulator med de fire grunnleggende regneartene, samt potens og kvadratrot."""

import math


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Kan ikke dele på null")
    return a / b


def power(a, b):
    return a**b


def sqrt(a):
    if a < 0:
        raise ValueError("Kan ikke ta kvadratroten av et negativt tall")
    return math.sqrt(a)
