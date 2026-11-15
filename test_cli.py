import subprocess
import sys
from pathlib import Path

import pytest

import cli


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
        ("1 / 0", "Kan ikke dele på null"),
        ("1 % 0", "Kan ikke ta modulo med null"),
        ("sqrt(-4)", "Kan ikke ta kvadratroten av et negativt tall"),
        ("0 ** -1", "Null kan ikke opphøyes i en negativ potens"),
        ("sqrt((-1) ** 0.5)", "Kan bare regne med reelle tall"),
        ("1e308 ** 2", "Tallet er for stort til å beregnes"),
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
    assert "Resultat: 5" in output.out
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
    assert "Resultat: 6" in output
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
    assert "Resultat: 5" in result.stdout
    assert "Feil: Kan ikke dele på null" in result.stdout
    assert "Resultat: 4" in result.stdout
    assert "Ha det!" in result.stdout
    assert result.stderr == ""
