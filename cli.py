"""Interaktiv kalkulator. Start med ``python cli.py`` og avslutt med ``q``."""

import ast
import math

import calc


OPERATIONS = {
    ast.Add: calc.add,
    ast.Sub: calc.subtract,
    ast.Mult: calc.multiply,
    ast.Div: calc.divide,
    ast.Mod: calc.modulo,
    ast.Pow: calc.power,
}


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
    try:
        operator, operands = parse_expression(expression)
    except ValueError:
        # Behold også uttrykk uten mellomrom, parenteser og sammensatte uttrykk.
        return calculate(expression)
    operation = calc.sqrt if operator == "sqrt" else BINARY_OPERATIONS[operator]
    return _validate_result(operation(*operands))


def _validate_result(result):
    if isinstance(result, complex):
        raise ValueError("Kan bare regne med reelle tall")
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Ugyldig tall. Bruk endelige tall.")
    return result


def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return _validate_result(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATIONS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and left == 0 and right < 0:
            raise ValueError("Null kan ikke opphøyes i en negativ potens")
        result = OPERATIONS[type(node.op)](left, right)
        return _validate_result(result)
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return _evaluate(node.operand)
        if isinstance(node.op, ast.USub):
            return calc.subtract(0, _evaluate(node.operand))
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "sqrt"
        and len(node.args) == 1
        and not node.keywords
    ):
        return _validate_result(calc.sqrt(_evaluate(node.args[0])))
    raise ValueError(
        "Bruk bare tall, parenteser, +, -, *, /, %, ** og sqrt(tall)"
    )


def calculate(expression):
    """Regn ut et uttrykk med funksjonene i calc, uten å kjøre Python-kode."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError(
            "Ugyldig regnestykke. Prøv for eksempel 2 + 3 eller sqrt(9)"
        ) from None
    return _evaluate(tree.body)


def main():
    """Les regnestykker til brukeren skriver q eller avslutter inndata."""
    print("Skriv et regnestykke, for eksempel 2 + 3 eller sqrt(9).")
    print("Regnearter: +, -, *, /, %, ** eller ^. Også sqrt 16. Skriv q for å avslutte.")
    while True:
        try:
            expression = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHa det!")
            return
        if expression.lower() == "q":
            print("Ha det!")
            return
        if not expression:
            continue
        try:
            result = evaluate_expression(expression)
        except ValueError as error:
            print(f"Feil: {error}")
        except ZeroDivisionError:
            print("Feil: Regnestykket innebærer deling på null (også ved modulo).")
        except OverflowError:
            print("Feil: Resultatet er for stort. Prøv mindre tall.")
        except RecursionError:
            print("Feil: Regnestykket er for komplisert")
        else:
            try:
                print(f"Svar: {result}")
            except ValueError:
                print("Feil: Tallet er for stort til å vises")


if __name__ == "__main__":
    main()
