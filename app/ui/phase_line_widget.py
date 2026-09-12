import numpy as np
import pyqtgraph as pg

from PySide6.QtCore import (
    QTimer,
    Signal,
)

from app.core.analysis.function_analysis import (
    function_value,
)

from app.core.analysis.one_dimensional_dynamics import (
    find_equilibria,
    flow_direction,
)


class PhaseLineWidget(pg.PlotWidget):

    initial_condition_selected = Signal(float)

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent=parent
        )

        # =================================================
        # STATE
        # =================================================

        self.current_expression = None

        self.x_min = -5.0
        self.x_max = 5.0

        self.flow_items = []
        self.equilibrium_labels = []

        # Animated background particles
        self.flow_particle_positions = np.array([])
        self.flow_particle_items = []

        # User-selected trajectory particle
        self.selected_x = None
        self.selected_active = False

        # =================================================
        # APPEARANCE
        # =================================================

        self.setBackground(
            "#0d1424"
        )

        self.setMinimumHeight(
            155
        )

        self.setMaximumHeight(
            185
        )

        self.setYRange(
            -1,
            1,
            padding=0,
        )

        self.setMouseEnabled(
            x=True,
            y=False,
        )

        self.hideAxis(
            "left"
        )

        bottom_axis = self.getAxis(
            "bottom"
        )

        bottom_axis.setPen(
            pg.mkPen(
                "#64748b",
                width=1,
            )
        )

        bottom_axis.setTextPen(
            pg.mkPen(
                "#94a3b8"
            )
        )

        # =================================================
        # CENTRAL PHASE LINE
        # =================================================

        self.phase_axis = pg.InfiniteLine(
            pos=0,
            angle=0,
            movable=False,
            pen=pg.mkPen(
                "#64748b",
                width=2,
            ),
        )

        self.addItem(
            self.phase_axis
        )

        # =================================================
        # EQUILIBRIUM MARKERS
        # =================================================

        self.stable_markers = pg.ScatterPlotItem(
            size=16,
            symbol="o",
            pen=pg.mkPen(
                "#e0f2fe",
                width=2,
            ),
            brush=pg.mkBrush(
                "#06b6d4"
            ),
        )

        self.unstable_markers = pg.ScatterPlotItem(
            size=16,
            symbol="o",
            pen=pg.mkPen(
                "#f87171",
                width=2.5,
            ),
            brush=None,
        )

        self.nonhyperbolic_markers = pg.ScatterPlotItem(
            size=16,
            symbol="d",
            pen=pg.mkPen(
                "#fbbf24",
                width=2,
            ),
            brush=pg.mkBrush(
                "#78350f"
            ),
        )

        self.addItem(
            self.stable_markers
        )

        self.addItem(
            self.unstable_markers
        )

        self.addItem(
            self.nonhyperbolic_markers
        )

        # =================================================
        # USER-SELECTED PARTICLE
        # =================================================

        self.selected_particle = pg.ScatterPlotItem(
            size=18,
            symbol="o",
            pen=pg.mkPen(
                "#ffffff",
                width=2.5,
            ),
            brush=pg.mkBrush(
                "#fbbf24"
            ),
        )

        self.selected_particle.setZValue(
            20
        )

        self.addItem(
            self.selected_particle
        )

        self.selected_particle.clear()

        # =================================================
        # ANIMATION TIMER
        # =================================================

        self.animation_timer = QTimer(
            self
        )

        self.animation_timer.setInterval(
            16
        )

        self.animation_timer.timeout.connect(
            self._animate
        )

        self.animation_timer.start()

        # =================================================
        # MOUSE
        # =================================================

        self.scene().sigMouseClicked.connect(
            self._mouse_clicked
        )

    # =====================================================
    # UPDATE COMPLETE PHASE LINE
    # =====================================================

    def update_phase_line(
        self,
        expression: str,
        x_min: float,
        x_max: float,
    ):

        self.current_expression = expression

        self.x_min = float(
            x_min
        )

        self.x_max = float(
            x_max
        )

        self.clear_dynamic_items()

        self.setXRange(
            self.x_min,
            self.x_max,
            padding=0.02,
        )

        equilibria = find_equilibria(
            expression,
            self.x_min,
            self.x_max,
        )

        stable_x = []
        unstable_x = []
        nonhyperbolic_x = []

        # -------------------------------------------------
        # Equilibria
        # -------------------------------------------------

        for equilibrium in equilibria:

            if (
                equilibrium.stability
                == "stable"
            ):

                stable_x.append(
                    equilibrium.x
                )

            elif (
                equilibrium.stability
                == "unstable"
            ):

                unstable_x.append(
                    equilibrium.x
                )

            else:

                nonhyperbolic_x.append(
                    equilibrium.x
                )

            label = pg.TextItem(
                text=(
                    f"{equilibrium.x:.3f}\n"
                    f"{equilibrium.stability}"
                ),
                anchor=(0.5, 1.3),
                color="#cbd5e1",
            )

            label.setPos(
                equilibrium.x,
                0,
            )

            self.addItem(
                label
            )

            self.equilibrium_labels.append(
                label
            )

        self.stable_markers.setData(
            stable_x,
            np.zeros(
                len(stable_x)
            ),
        )

        self.unstable_markers.setData(
            unstable_x,
            np.zeros(
                len(unstable_x)
            ),
        )

        self.nonhyperbolic_markers.setData(
            nonhyperbolic_x,
            np.zeros(
                len(nonhyperbolic_x)
            ),
        )

        # -------------------------------------------------
        # Static direction arrows
        # -------------------------------------------------

        sample_positions = np.linspace(
            self.x_min,
            self.x_max,
            17,
        )

        for x_value in sample_positions:

            too_close = any(
                abs(
                    x_value
                    - equilibrium.x
                )
                < (
                    self.x_max
                    - self.x_min
                ) * 0.025

                for equilibrium
                in equilibria
            )

            if too_close:
                continue

            direction = flow_direction(
                expression,
                float(x_value),
            )

            if direction > 0:

                arrow_text = "→"
                arrow_color = "#34d399"

            elif direction < 0:

                arrow_text = "←"
                arrow_color = "#c084fc"

            else:
                continue

            arrow = pg.TextItem(
                text=arrow_text,
                anchor=(0.5, 0.5),
                color=arrow_color,
            )

            arrow.setPos(
                float(x_value),
                0.15,
            )

            self.addItem(
                arrow
            )

            self.flow_items.append(
                arrow
            )

        # -------------------------------------------------
        # Create animated flow particles
        # -------------------------------------------------

        self._create_flow_particles()

        # Parameter/equation changes reset the
        # user-selected trajectory particle.
        self.selected_active = False
        self.selected_x = None

        self.selected_particle.clear()

    # =====================================================
    # CREATE ANIMATED FLOW PARTICLES
    # =====================================================

    def _create_flow_particles(
        self,
    ):

        for item in (
            self.flow_particle_items
        ):

            self.removeItem(
                item
            )

        self.flow_particle_items = []

        number_of_particles = 15

        self.flow_particle_positions = (
            np.linspace(
                self.x_min,
                self.x_max,
                number_of_particles,
            )
        )

        for index in range(
            number_of_particles
        ):

            particle = pg.ScatterPlotItem(
                size=7,
                symbol="o",
                pen=None,
                brush=pg.mkBrush(
                    103,
                    232,
                    249,
                    160,
                ),
            )

            particle.setZValue(
                5
            )

            self.addItem(
                particle
            )

            self.flow_particle_items.append(
                particle
            )

    # =====================================================
    # ANIMATION
    # =====================================================

    def _animate(
        self,
    ):

        if not self.current_expression:
            return

        self._animate_flow_particles()
        self._animate_selected_particle()

    # =====================================================
    # BACKGROUND FLOW ANIMATION
    # =====================================================

    def _animate_flow_particles(
        self,
    ):

        if (
            len(
                self.flow_particle_positions
            )
            == 0
        ):
            return

        domain_width = (
            self.x_max
            - self.x_min
        )

        # Visual integration time step.
        frame_scale = self.animation_timer.interval() / 33.0
        dt = 0.018 * frame_scale

        maximum_step = (
            domain_width
            * 0.012 * frame_scale
        )

        for index, x_value in enumerate(
            self.flow_particle_positions
        ):

            try:

                velocity = function_value(
                    self.current_expression,
                    float(x_value),
                )

            except Exception:
                continue

            if not np.isfinite(
                velocity
            ):
                continue

            displacement = (
                velocity * dt
            )

            # Prevent extremely large vector fields
            # from teleporting visual particles.
            displacement = float(
                np.clip(
                    displacement,
                    -maximum_step,
                    maximum_step,
                )
            )

            new_x = (
                x_value
                + displacement
            )

            # If particle leaves the visible domain,
            # recycle it to the opposite side.
            if new_x > self.x_max:

                new_x = self.x_min

            elif new_x < self.x_min:

                new_x = self.x_max

            self.flow_particle_positions[
                index
            ] = new_x

            # Velocity also controls particle opacity.
            speed = abs(
                velocity
            )

            alpha = int(
                np.clip(
                    90 + speed * 35,
                    90,
                    230,
                )
            )

            particle = (
                self.flow_particle_items[
                    index
                ]
            )

            if velocity >= 0:

                particle.setBrush(
                    pg.mkBrush(
                        52,
                        211,
                        153,
                        alpha,
                    )
                )

            else:

                particle.setBrush(
                    pg.mkBrush(
                        192,
                        132,
                        252,
                        alpha,
                    )
                )

            particle.setData(
                [new_x],
                [0],
            )

    # =====================================================
    # USER-SELECTED PARTICLE ANIMATION
    # =====================================================

    def _animate_selected_particle(
        self,
    ):

        if not self.selected_active:
            return

        if self.selected_x is None:
            return

        try:

            velocity = function_value(
                self.current_expression,
                self.selected_x,
            )

        except Exception:

            self.selected_active = False
            return

        if not np.isfinite(
            velocity
        ):

            self.selected_active = False
            return

        domain_width = (
            self.x_max
            - self.x_min
        )

        frame_scale = self.animation_timer.interval() / 33.0
        dt = 0.012 * frame_scale

        maximum_step = (
            domain_width
            * 0.008 * frame_scale
        )

        displacement = float(
            np.clip(
                velocity * dt,
                -maximum_step,
                maximum_step,
            )
        )

        self.selected_x += (
            displacement
        )

        # Stop if trajectory leaves current view.
        if (
            self.selected_x
            < self.x_min

            or self.selected_x
            > self.x_max
        ):

            self.selected_active = False
            self.selected_particle.clear()

            return

        self.selected_particle.setData(
            [self.selected_x],
            [0],
        )

        # As velocity becomes tiny near an
        # equilibrium, the particle naturally
        # appears to settle there.
        if abs(velocity) < 1e-5:

            self.selected_active = False

    # =====================================================
    # CLICK INITIAL CONDITION
    # =====================================================

    def _mouse_clicked(
        self,
        event,
    ):

        mouse_position = (
            event.scenePos()
        )

        view_box = (
            self.getViewBox()
        )

        if not (
            view_box
            .sceneBoundingRect()
            .contains(
                mouse_position
            )
        ):

            return

        graph_position = (
            view_box.mapSceneToView(
                mouse_position
            )
        )

        x_value = float(
            graph_position.x()
        )

        self.selected_x = (
            x_value
        )

        self.selected_active = True

        self.selected_particle.setData(
            [x_value],
            [0],
        )

        self.initial_condition_selected.emit(
            x_value
        )

    # =====================================================
    # CLEAN DYNAMIC ITEMS
    # =====================================================

    def clear_dynamic_items(
        self,
    ):

        for item in (
            self.flow_items
        ):

            self.removeItem(
                item
            )

        self.flow_items = []

        for label in (
            self.equilibrium_labels
        ):

            self.removeItem(
                label
            )

        self.equilibrium_labels = []

        for item in (
            self.flow_particle_items
        ):

            self.removeItem(
                item
            )

        self.flow_particle_items = []

        self.flow_particle_positions = (
            np.array([])
        )

        self.stable_markers.clear()
        self.unstable_markers.clear()
        self.nonhyperbolic_markers.clear()
