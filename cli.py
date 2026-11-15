"""Interaktiv kalkulator. Start med ``python cli.py`` og avslutt med ``q``."""

import math

import calc


BINARY_OPERATIONS = {
    "+": calc.add,
    "-": calc.subtract,
    "*": calc.multiply,
    "/": calc.divide,
    "%": calc.modulo,
    "^": calc.power,
}


def parse_expression(expression):
    """Returner regneart og tall fra et binært uttrykk eller ``sqrt tall``."""
    parts = expression.split()
    if len(parts) == 2 and parts[0] == "sqrt":
        operator, numbers = "sqrt", parts[1:]
    elif len(parts) == 3 and parts[1] in BINARY_OPERATIONS:
        operator, numbers = parts[1], (parts[0], parts[2])
    else:
        raise ValueError(
            "Ugyldig regnestykke. Bruk mellomrom, for eksempel '10 + 3', "
            "'2 ^ 8', 'sqrt 16' eller '10 % 3'."
        )

    try:
        operands = tuple(float(number) for number in numbers)
    except ValueError:
        raise ValueError("Ugyldig tall. Bruk tall som 10, -3 eller 2.5.") from None
    if not all(math.isfinite(number) for number in operands):
        raise ValueError("Ugyldig tall. Bruk endelige tall.")
    return operator, operands


def evaluate_expression(expression):
    """Tolk regnestykket og beregn svaret med funksjonene i calc."""
    operator, operands = parse_expression(expression)
    operation = calc.sqrt if operator == "sqrt" else BINARY_OPERATIONS[operator]
    return operation(*operands)


def main():
    print("Kalkulator: Bruk +, -, *, /, %, ^ eller sqrt. Skriv q for å avslutte.")
    while True:
        try:
            expression = input("Skriv et regnestykke: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if expression == "q":
            break
        try:
            result = evaluate_expression(expression)
        except ValueError as error:
            print(f"Feil: {error}")
        except ZeroDivisionError:
            print("Feil: Regnestykket innebærer deling på null (også ved modulo).")
        except OverflowError:
            print("Feil: Resultatet er for stort. Prøv mindre tall.")
        else:
            print(f"Svar: {result}")


if __name__ == "__main__":
    main()
