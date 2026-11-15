"""Interaktiv kalkulator. Start med ``python cli.py`` og avslutt med q."""

import ast

import calc


OPERATIONS = {
    ast.Add: calc.add,
    ast.Sub: calc.subtract,
    ast.Mult: calc.multiply,
    ast.Div: calc.divide,
    ast.Mod: calc.modulo,
    ast.Pow: calc.power,
}


def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATIONS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and left == 0 and right < 0:
            raise ValueError("Null kan ikke opphøyes i en negativ potens")
        result = OPERATIONS[type(node.op)](left, right)
        if isinstance(result, complex):
            raise ValueError("Kan bare regne med reelle tall")
        return result
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
        return calc.sqrt(_evaluate(node.args[0]))
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
    print("Regnearter: +, -, *, /, %, **. Skriv q for å avslutte.")
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
            result = calculate(expression)
        except (ValueError, ZeroDivisionError) as error:
            print(f"Feil: {error}")
        except OverflowError:
            print("Feil: Tallet er for stort til å beregnes")
        except RecursionError:
            print("Feil: Regnestykket er for komplisert")
        else:
            try:
                print(f"Resultat: {result}")
            except ValueError:
                print("Feil: Tallet er for stort til å vises")


if __name__ == "__main__":
    main()
