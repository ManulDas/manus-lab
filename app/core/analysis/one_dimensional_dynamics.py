from dataclasses import dataclass

from app.core.analysis.function_analysis import (
    find_roots,
    function_value,
    numerical_derivative,
)


@dataclass(frozen=True)
class Equilibrium1D:
    x: float
    derivative: float
    stability: str


def classify_equilibrium(
    expression: str,
    x_value: float,
    tolerance: float = 1e-5,
) -> Equilibrium1D:

    derivative = numerical_derivative(
        expression,
        x_value,
    )

    if derivative < -tolerance:
        stability = "stable"

    elif derivative > tolerance:
        stability = "unstable"

    else:
        stability = "non-hyperbolic"

    return Equilibrium1D(
        x=float(x_value),
        derivative=float(derivative),
        stability=stability,
    )


def find_equilibria(
    expression: str,
    x_min: float,
    x_max: float,
) -> list[Equilibrium1D]:

    roots = find_roots(
        expression,
        x_min,
        x_max,
    )

    equilibria = []

    for root in roots:

        equilibrium = classify_equilibrium(
            expression,
            root,
        )

        equilibria.append(
            equilibrium
        )

    return equilibria


def flow_direction(
    expression: str,
    x_value: float,
    tolerance: float = 1e-8,
) -> int:

    velocity = function_value(
        expression,
        x_value,
    )

    if velocity > tolerance:
        return 1

    if velocity < -tolerance:
        return -1

    return 0