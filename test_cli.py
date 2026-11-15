"""Tester for parsing, beregning og feilhåndtering i kommandolinjeprogrammet."""

import subprocess
import sys
from pathlib import Path

import pytest

from cli import evaluate_expression, main, parse_expression


@pytest.mark.parametrize(
    "expression, operator, operands",
    [
        ("10 + 3", "+", (10, 3)),
        ("2 ^ 8", "^", (2, 8)),
        ("sqrt 16", "sqrt", (16,)),
        ("10 % 3", "%", (10, 3)),
        ("  -2.5\t*  +4  ", "*", (-2.5, 4)),
        ("1e2 / 2", "/", (100, 2)),
    ],
)
def test_parse_expression(expression, operator, operands):
    assert parse_expression(expression) == (operator, operands)


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("10 + 3", 13),
        ("10 - 3", 7),
        ("-2.5 * 4", -10),
        ("10 / 4", 2.5),
        ("2 ^ 8", 256),
        ("2 ^ -2", 0.25),
        ("sqrt 16", 4),
        ("sqrt 0", 0),
        ("10 % 3", 1),
    ],
)
def test_evaluate_expression(expression, expected):
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression",
    ["", " ", "10 +", "1 + 2 + 3", "sqrt", "sqrt 1 2", "10 & 3", "10+3"],
)
def test_reject_invalid_syntax(expression):
    with pytest.raises(ValueError, match="Ugyldig regnestykke"):
        parse_expression(expression)


@pytest.mark.parametrize(
    "expression", ["hei + 3", "sqrt hei", "1 + to", "nan + 1", "sqrt inf", "1e999 + 1"]
)
def test_reject_invalid_numbers(expression):
    with pytest.raises(ValueError, match="Ugyldig tall"):
        parse_expression(expression)


@pytest.mark.parametrize(
    "expression, exception",
    [("10 / 0", ZeroDivisionError), ("10 % 0", ZeroDivisionError), ("sqrt -1", ValueError)],
)
def test_calculation_errors(expression, exception):
    with pytest.raises(exception):
        evaluate_expression(expression)


@pytest.mark.parametrize(
    "expression, message",
    [
        ("ugyldig", "Ugyldig regnestykke"),
        ("hei + 1", "Ugyldig tall"),
        ("10 / 0", "Regnestykket innebærer deling på null"),
        ("10 % 0", "Regnestykket innebærer deling på null"),
        ("0 ^ -1", "Regnestykket innebærer deling på null"),
        ("sqrt -1", "Kan ikke ta kvadratroten av et negativt tall"),
        ("10 ^ 1000", "Resultatet er for stort"),
    ],
)
def test_main_continues_after_errors(monkeypatch, capsys, expression, message):
    answers = iter([expression, "10 + 3", " q "])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    main()

    output = capsys.readouterr().out
    assert f"Feil: {message}" in output
    assert "Svar: 13.0" in output


@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_main_handles_closed_or_interrupted_input(monkeypatch, capsys, exception):
    def interrupted_input(prompt):
        raise exception

    monkeypatch.setattr("builtins.input", interrupted_input)
    main()
    assert "Feil:" not in capsys.readouterr().out


def test_script_runs_until_q():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("cli.py"))],
        input="10 + 3\n2 ^ 8\nsqrt 16\n10 % 3\nq\n99 + 1\n",
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    for expected in ("13.0", "256.0", "4.0", "1.0"):
        assert f"Svar: {expected}" in result.stdout
    assert "Svar: 100" not in result.stdout
