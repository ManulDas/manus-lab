import ast
import numpy as np


class ExpressionError(ValueError):
    """Readable error for invalid mathematical expressions."""
    pass


ALLOWED_FUNCTIONS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
}

ALLOWED_CONSTANTS = {
    "pi": np.pi,
    "e": np.e,
}


def detect_parameters(expression: str) -> list[str]:
    """
    Detect free symbols in an expression.

    Example:
        r*x - x**3  ->  ["r"]
        a*x + b     ->  ["a", "b"]
    """

    try:
        tree = ast.parse(
            expression,
            mode="eval",
        )

    except SyntaxError as error:
        raise ExpressionError(
            "Invalid mathematical syntax."
        ) from error

    names = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if not isinstance(
                node.func,
                ast.Name,
            ):
                raise ExpressionError(
                    "Invalid function call."
                )

            if (
                node.func.id
                not in ALLOWED_FUNCTIONS
            ):
                raise ExpressionError(
                    f"Unknown function: "
                    f"{node.func.id}"
                )

        if isinstance(
            node,
            ast.Name,
        ):
            names.add(
                node.id
            )

    excluded = (
        {"x"}
        | set(ALLOWED_FUNCTIONS)
        | set(ALLOWED_CONSTANTS)
    )

    parameters = (
        names - excluded
    )

    return sorted(
        parameters
    )


def resolve_parameters(
    expression: str,
    parameters: dict[str, float],
) -> str:
    """
    Replace parameter symbols safely with numerical values.

    Example:
        r*x - x**3, {"r": 2}
        becomes approximately
        2.0*x - x**3
    """

    required = detect_parameters(
        expression
    )

    missing = [
        name
        for name in required
        if name not in parameters
    ]

    if missing:
        raise ExpressionError(
            "Missing parameter value(s): "
            + ", ".join(missing)
        )

    try:
        tree = ast.parse(
            expression,
            mode="eval",
        )

    except SyntaxError as error:
        raise ExpressionError(
            "Invalid mathematical syntax."
        ) from error

    class ParameterReplacer(
        ast.NodeTransformer
    ):

        def visit_Name(
            self,
            node,
        ):

            if node.id in parameters:

                return ast.copy_location(
                    ast.Constant(
                        value=float(
                            parameters[
                                node.id
                            ]
                        )
                    ),
                    node,
                )

            return node

    tree = ParameterReplacer().visit(
        tree
    )

    ast.fix_missing_locations(
        tree
    )

    return ast.unparse(
        tree
    )


def evaluate_expression(
    expression: str,
    x: np.ndarray,
) -> np.ndarray:

    try:
        tree = ast.parse(
            expression,
            mode="eval",
        )

    except SyntaxError as error:
        raise ExpressionError(
            "Invalid mathematical syntax."
        ) from error

    try:

        with np.errstate(
            all="ignore"
        ):

            result = _evaluate_node(
                tree.body,
                x,
            )

    except ExpressionError:
        raise

    except Exception as error:
        raise ExpressionError(
            str(error)
        ) from error

    result = np.asarray(
        result,
        dtype=float,
    )

    if result.ndim == 0:

        result = np.full_like(
            x,
            float(result),
            dtype=float,
        )

    try:

        result = np.broadcast_to(
            result,
            x.shape,
        )

    except ValueError as error:

        raise ExpressionError(
            "Expression did not produce "
            "values compatible with x."
        ) from error

    return result


def _evaluate_node(
    node,
    x,
):

    if isinstance(
        node,
        ast.Constant,
    ):

        if isinstance(
            node.value,
            (int, float),
        ):
            return node.value

        raise ExpressionError(
            "Only numerical constants "
            "are allowed."
        )

    if isinstance(
        node,
        ast.Name,
    ):

        if node.id == "x":
            return x

        if (
            node.id
            in ALLOWED_CONSTANTS
        ):

            return (
                ALLOWED_CONSTANTS[
                    node.id
                ]
            )

        raise ExpressionError(
            f"Unknown symbol: {node.id}"
        )

    if isinstance(
        node,
        ast.BinOp,
    ):

        left = _evaluate_node(
            node.left,
            x,
        )

        right = _evaluate_node(
            node.right,
            x,
        )

        if isinstance(
            node.op,
            ast.Add,
        ):
            return left + right

        if isinstance(
            node.op,
            ast.Sub,
        ):
            return left - right

        if isinstance(
            node.op,
            ast.Mult,
        ):
            return left * right

        if isinstance(
            node.op,
            ast.Div,
        ):
            return left / right

        if isinstance(
            node.op,
            ast.Pow,
        ):
            return left ** right

        raise ExpressionError(
            "That mathematical operator "
            "is not allowed."
        )

    if isinstance(
        node,
        ast.UnaryOp,
    ):

        value = _evaluate_node(
            node.operand,
            x,
        )

        if isinstance(
            node.op,
            ast.USub,
        ):
            return -value

        if isinstance(
            node.op,
            ast.UAdd,
        ):
            return value

        raise ExpressionError(
            "That unary operator "
            "is not allowed."
        )

    if isinstance(
        node,
        ast.Call,
    ):

        if not isinstance(
            node.func,
            ast.Name,
        ):
            raise ExpressionError(
                "Invalid function."
            )

        function_name = (
            node.func.id
        )

        if (
            function_name
            not in ALLOWED_FUNCTIONS
        ):

            raise ExpressionError(
                f"Unknown function: "
                f"{function_name}"
            )

        if len(node.args) != 1:

            raise ExpressionError(
                f"{function_name} must "
                f"have exactly one argument."
            )

        argument = _evaluate_node(
            node.args[0],
            x,
        )

        return (
            ALLOWED_FUNCTIONS[
                function_name
            ](
                argument
            )
        )

    raise ExpressionError(
        "This expression contains "
        "an unsupported operation."
    )