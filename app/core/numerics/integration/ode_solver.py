from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from app.core.analysis.function_analysis import (
    function_value,
)


@dataclass(frozen=True)
class SimulationConfig:
    t_start: float = 0.0
    t_end: float = 10.0

    num_points: int = 1000

    method: str = "RK45"

    rtol: float = 1e-7
    atol: float = 1e-9


@dataclass(frozen=True)
class Trajectory:
    t: np.ndarray
    y: np.ndarray

    success: bool
    message: str

    method: str


def integrate_ode(
    rhs,
    initial_state,
    config: SimulationConfig,
) -> Trajectory:

    if config.t_end <= config.t_start:
        raise ValueError(
            "Simulation end time must be greater "
            "than the start time."
        )

    if config.num_points < 2:
        raise ValueError(
            "Simulation requires at least two points."
        )

    initial_state = np.asarray(
        initial_state,
        dtype=float,
    )

    t_eval = np.linspace(
        config.t_start,
        config.t_end,
        config.num_points,
    )

    solution = solve_ivp(
        rhs,
        (
            config.t_start,
            config.t_end,
        ),
        initial_state,
        method=config.method,
        t_eval=t_eval,
        rtol=config.rtol,
        atol=config.atol,
    )

    if solution.y.size == 0:
        raise RuntimeError(
            "ODE solver returned no trajectory."
        )

    if not np.all(
        np.isfinite(solution.y)
    ):
        raise RuntimeError(
            "Trajectory contains NaN or infinite values."
        )

    return Trajectory(
        t=solution.t,
        y=solution.y,
        success=solution.success,
        message=solution.message,
        method=config.method,
    )


def integrate_1d_expression(
    expression: str,
    x0: float,
    config: SimulationConfig,
) -> Trajectory:

    def rhs(
        t,
        state,
    ):

        x_value = float(
            state[0]
        )

        dxdt = function_value(
            expression,
            x_value,
        )

        if not np.isfinite(
            dxdt
        ):
            raise RuntimeError(
                "The vector field became non-finite "
                "during integration."
            )

        return [
            dxdt
        ]

    return integrate_ode(
        rhs=rhs,
        initial_state=[
            float(x0)
        ],
        config=config,
    )