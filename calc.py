"""Enkel kalkulator med de fire grunnleggende regneartene."""


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
