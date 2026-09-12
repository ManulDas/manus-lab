import numpy as np

from scipy.integrate import quad
from scipy.optimize import brentq

from app.core.expressions.simple_parser import (
    ExpressionError,
    evaluate_expression,
)


def function_value(expression: str, x_value: float) -> float:
    x = np.array([x_value], dtype=float)

    y = evaluate_expression(
        expression,
        x,
    )

    return float(y[0])


def numerical_derivative(
    expression: str,
    x_value: float,
) -> float:
    """
    Central-difference estimate of f'(x).
    """

    h = max(
        1e-6,
        abs(x_value) * 1e-5,
    )

    y_plus = function_value(
        expression,
        x_value + h,
    )

    y_minus = function_value(
        expression,
        x_value - h,
    )

    return (
        y_plus - y_minus
    ) / (2 * h)


def numerical_second_derivative(
    expression: str,
    x_value: float,
) -> float:
    """
    Central-difference estimate of f''(x).
    """

    h = max(
        1e-4,
        abs(x_value) * 1e-4,
    )

    y_plus = function_value(
        expression,
        x_value + h,
    )

    y = function_value(
        expression,
        x_value,
    )

    y_minus = function_value(
        expression,
        x_value - h,
    )

    return (
        y_plus
        - 2 * y
        + y_minus
    ) / (h ** 2)


def derivative_values(
    expression: str,
    x: np.ndarray,
) -> np.ndarray:
    """
    Vectorised numerical derivative for plotting f'(x).
    """

    x = np.asarray(
        x,
        dtype=float,
    )

    h = np.maximum(
        1e-6,
        np.abs(x) * 1e-5,
    )

    y_plus = evaluate_expression(
        expression,
        x + h,
    )

    y_minus = evaluate_expression(
        expression,
        x - h,
    )

    return (
        y_plus - y_minus
    ) / (2 * h)


def find_roots(
    expression: str,
    x_min: float,
    x_max: float,
    samples: int = 2001,
) -> list[float]:
    """
    Find roots numerically over a finite interval.
    """

    x = np.linspace(
        x_min,
        x_max,
        samples,
    )

    y = evaluate_expression(
        expression,
        x,
    )

    roots = []

    def add_root(root):
        if not np.isfinite(root):
            return

        # Prevent duplicate roots.
        for existing in roots:
            if abs(existing - root) < 1e-4:
                return

        try:
            residual = abs(
                function_value(
                    expression,
                    root,
                )
            )
        except Exception:
            return

        # Helps reject false roots caused by discontinuities.
        if residual < 1e-5:
            roots.append(float(root))

    for index in range(len(x) - 1):

        x1 = x[index]
        x2 = x[index + 1]

        y1 = y[index]
        y2 = y[index + 1]

        if not (
            np.isfinite(y1)
            and np.isfinite(y2)
        ):
            continue

        if abs(y1) < 1e-8:
            add_root(x1)

        if y1 * y2 < 0:
            try:
                root = brentq(
                    lambda value: function_value(
                        expression,
                        value,
                    ),
                    x1,
                    x2,
                )

                add_root(root)

            except Exception:
                pass

    if np.isfinite(y[-1]) and abs(y[-1]) < 1e-8:
        add_root(x[-1])

    return sorted(roots)


def find_extrema(
    expression: str,
    x_min: float,
    x_max: float,
    samples: int = 2001,
):
    """
    Find local minima and maxima by locating roots of f'(x).
    """

    x = np.linspace(
        x_min,
        x_max,
        samples,
    )

    derivative = derivative_values(
        expression,
        x,
    )

    extrema = []

    def add_extremum(x_value):
        for existing in extrema:
            if abs(
                existing["x"] - x_value
            ) < 1e-4:
                return

        try:
            y_value = function_value(
                expression,
                x_value,
            )

            second = numerical_second_derivative(
                expression,
                x_value,
            )

        except Exception:
            return

        if not (
            np.isfinite(y_value)
            and np.isfinite(second)
        ):
            return

        if second > 1e-5:
            kind = "minimum"

        elif second < -1e-5:
            kind = "maximum"

        else:
            kind = "stationary"

        extrema.append(
            {
                "x": float(x_value),
                "y": float(y_value),
                "kind": kind,
            }
        )

    for index in range(
        len(x) - 1
    ):

        x1 = x[index]
        x2 = x[index + 1]

        d1 = derivative[index]
        d2 = derivative[index + 1]

        if not (
            np.isfinite(d1)
            and np.isfinite(d2)
        ):
            continue

        if abs(d1) < 1e-8:
            add_extremum(x1)

        if d1 * d2 < 0:
            try:
                stationary_point = brentq(
                    lambda value: numerical_derivative(
                        expression,
                        value,
                    ),
                    x1,
                    x2,
                )

                add_extremum(
                    stationary_point
                )

            except Exception:
                pass

    return sorted(
        extrema,
        key=lambda item: item["x"],
    )


def definite_integral(
    expression: str,
    a: float,
    b: float,
):
    """
    Numerically integrate f(x) from a to b.
    """

    value, error = quad(
        lambda x: function_value(
            expression,
            x,
        ),
        a,
        b,
        limit=200,
    )

    return float(value), float(error)