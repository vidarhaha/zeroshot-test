"""Tester for begge uttrykksformatene og den interaktive kalkulatoren."""

import subprocess
import sys
from pathlib import Path

import pytest

import cli
from cli import evaluate_expression, main, parse_expression


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2 + 3", 5),
        ("5-8", -3),
        ("4 * 3", 12),
        ("7 / 2", 3.5),
        ("10 % 3", 1),
        ("2 ** 3", 8),
        ("sqrt(9)", 3),
        ("  -2.5 + +4  ", 1.5),
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("2 ** 3 ** 2", 512),
        ("sqrt(4 + 5) + 1", 4),
    ],
)
def test_calculate(expression, expected):
    assert cli.calculate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "2 +",
        "(2 + 3",
        "ukjent",
        "True + 1",
        "'2' + '3'",
        "[1, 2]",
        "2 // 1",
        "2 ^ 3",
        "sqrt()",
        "sqrt(1, 2)",
        "sqrt(a=4)",
        "calc.add(2, 3)",
        "__import__('os')",
    ],
)
def test_rejects_invalid_or_unsupported_expressions(expression):
    with pytest.raises(ValueError, match="Ugyldig regnestykke|Bruk bare tall"):
        cli.calculate(expression)


@pytest.mark.parametrize(
    "expression, message",
    [
        ("1 / 0", "Regnestykket innebærer deling på null"),
        ("1 % 0", "Regnestykket innebærer deling på null"),
        ("sqrt(-4)", "Kan ikke ta kvadratroten av et negativt tall"),
        ("0 ** -1", "Null kan ikke opphøyes i en negativ potens"),
        ("sqrt((-1) ** 0.5)", "Kan bare regne med reelle tall"),
        ("1e308 ** 2", "Resultatet er for stort"),
        ("2 +", "Ugyldig regnestykke"),
        ("hei", "Bruk bare tall"),
    ],
)
def test_main_reports_norwegian_errors_and_continues(
    expression, message, monkeypatch, capsys
):
    answers = iter([expression, "2 + 3", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    cli.main()

    output = capsys.readouterr()
    assert f"Feil: {message}" in output.out
    assert "Svar: 5" in output.out
    assert "Ha det!" in output.out
    assert output.err == ""


def test_main_handles_numbers_too_large_to_display(monkeypatch, capsys):
    previous_limit = sys.get_int_max_str_digits()
    # Begrensningen gjelder hele prosessen og må gjenopprettes etter testen.
    sys.set_int_max_str_digits(640)
    try:
        answers = iter(["10 ** 700", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

        cli.main()

        assert "Feil: Tallet er for stort til å vises" in capsys.readouterr().out
    finally:
        sys.set_int_max_str_digits(previous_limit)


@pytest.mark.parametrize("quit_command", ["q", "Q", "  q  "])
def test_main_quits_without_reading_more_input(quit_command, monkeypatch, capsys):
    answers = iter([quit_command])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    cli.main()

    assert "Ha det!" in capsys.readouterr().out


def test_main_ignores_blank_lines(monkeypatch, capsys):
    answers = iter(["", "   ", "2 * 3", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    cli.main()

    output = capsys.readouterr().out
    assert "Svar: 6" in output
    assert "Feil:" not in output


@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_main_handles_end_of_input(exception, monkeypatch, capsys):
    def end_input(prompt):
        raise exception

    monkeypatch.setattr("builtins.input", end_input)

    cli.main()

    output = capsys.readouterr()
    assert "Ha det!" in output.out
    assert output.err == ""


def test_script_runs_interactively():
    result = subprocess.run(
        [sys.executable, str(Path(cli.__file__))],
        input="2 + 3\n1 / 0\nsqrt(16)\nq\n",
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert "Svar: 5" in result.stdout
    assert "Feil: Regnestykket innebærer deling på null" in result.stdout
    assert "Svar: 4" in result.stdout
    assert "Ha det!" in result.stdout
    assert result.stderr == ""


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
        ("ugyldig", "Bruk bare tall"),
        ("hei + 1", "Bruk bare tall"),
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


@pytest.mark.parametrize(
    "expression",
    ["1e400", "sqrt(1e999)", "1e308+1e308", "1e308 + 1e308", "sqrt inf"],
)
def test_main_rejects_nonfinite_numbers_in_both_formats(
    expression, monkeypatch, capsys
):
    answers = iter([expression, "2+3", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    main()

    output = capsys.readouterr()
    assert "Feil:" in output.out
    assert "Svar: 5" in output.out
    assert output.err == ""


def test_script_accepts_both_expression_formats_in_one_session():
    result = subprocess.run(
        [sys.executable, str(Path(cli.__file__))],
        input="2 ^ 8\nsqrt 16\n2+3*4\n(2 + 3) * 4\nsqrt(4 + 5)\nQ\n99 + 1\n",
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    for expected in ("256.0", "4.0", "14", "20", "3.0"):
        assert f"Svar: {expected}" in result.stdout
    assert "Feil:" not in result.stdout
    assert "Ha det!" in result.stdout
    assert "Svar: 100" not in result.stdout
