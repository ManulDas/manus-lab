import numpy as np
import pyqtgraph as pg

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QFrame,
    QSplitter,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QCheckBox,
    QWidget,
)

from app.core.expressions.simple_parser import (
    ExpressionError,
    evaluate_expression,
    detect_parameters,
    resolve_parameters,

)
from app.ui.parameter_panel import ParameterPanel
from app.ui.phase_line_widget import PhaseLineWidget
from app.ui.phase_range_panel import PhaseRangePanel
from app.ui.time_series_widget import TimeSeriesWidget
from app.ui.presentation import AnimatedButton, AnimatedSwitch, mount_presentation

from app.core.numerics.integration.ode_solver import (
    SimulationConfig,
    integrate_1d_expression,
)

from app.core.analysis.function_analysis import (
    definite_integral,
    derivative_values,
    find_extrema,
    find_roots,
    function_value,
    numerical_derivative,
    numerical_second_derivative,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(antialias=True)

        self.setWindowTitle("Dynamical Systems Lab")
        self.resize(1100, 750)

        self.current_expression = ""

        self.plot_x = np.array([])
        self.plot_y = np.array([])

        self.analysis_labels = []
        self.integral_items = []

        # =================================================
        # EQUATION CONTROLS
        # =================================================

        self.equation_label = QLabel("y =")

        self.equation_input = QLineEdit()
        self.equation_input.setText("x**2")
        self.equation_input.setPlaceholderText(
            "Enter expression, e.g. x**3 - x"
        )

        self.plot_button = AnimatedButton("Plot")

        # =================================================
        # ANALYSIS MENU
        # =================================================

        self.analysis_button = AnimatedButton("Analysis")

        self.analysis_menu = QMenu(self)

        self.analysis_button.setMenu(
            self.analysis_menu
        )

        # Tangent line
        self.tangent_action = QAction(
            "Show tangent line",
            self,
        )

        self.tangent_action.setCheckable(True)

        self.analysis_menu.addAction(
            self.tangent_action
        )

        # Second derivative
        self.second_derivative_action = QAction(
            "Show second derivative f''(x)",
            self,
        )

        self.second_derivative_action.setCheckable(
            True
        )

        self.analysis_menu.addAction(
            self.second_derivative_action
        )

        self.analysis_menu.addSeparator()

        # Derivative curve
        self.derivative_curve_action = QAction(
            "Show derivative curve f'(x)",
            self,
        )

        self.derivative_curve_action.setCheckable(
            True
        )

        self.analysis_menu.addAction(
            self.derivative_curve_action
        )

        # Roots
        self.roots_action = QAction(
            "Show roots / zeros",
            self,
        )

        self.roots_action.setCheckable(True)

        self.analysis_menu.addAction(
            self.roots_action
        )

        # Extrema
        self.extrema_action = QAction(
            "Show local extrema",
            self,
        )

        self.extrema_action.setCheckable(True)

        self.analysis_menu.addAction(
            self.extrema_action
        )

        self.analysis_menu.addSeparator()

        # Integral
        self.integral_action = QAction(
            "Definite integral...",
            self,
        )

        self.analysis_menu.addAction(
            self.integral_action
        )

        self.clear_integral_action = QAction(
            "Clear integral",
            self,
        )

        self.analysis_menu.addAction(
            self.clear_integral_action
        )

        # =================================================
        # TOP CONTROL LAYOUT
        # =================================================

        
        # =================================================
        # LEFT CONTROL PANEL
        # =================================================

        self.left_panel = QFrame()
        self.left_panel.setObjectName("Sidebar")

        self.left_panel.setMinimumWidth(250)
        self.left_panel.setMaximumWidth(310)

        sidebar_layout = QVBoxLayout(
            self.left_panel
        )

        sidebar_layout.setContentsMargins(
            20,
            24,
            20,
            24,
        )

        sidebar_layout.setSpacing(14)


        # -------------------------------------------------
        # Function section
        # -------------------------------------------------

        function_title = QLabel(
            "FUNCTION"
        )

        function_title.setObjectName(
            "SectionTitle"
        )

        sidebar_layout.addWidget(
            function_title
        )


        equation_row = QHBoxLayout()

        equation_row.setSpacing(8)

        equation_row.addWidget(
            self.equation_label
        )

        equation_row.addWidget(
            self.equation_input
        )

        sidebar_layout.addLayout(
            equation_row
        )


        self.plot_button.setMinimumHeight(
            42
        )

        sidebar_layout.addWidget(
            self.plot_button
        )
        self.parameter_panel = ParameterPanel()
        self.phase_range_panel = PhaseRangePanel()

        sidebar_layout.addSpacing(
            12
        )

        sidebar_layout.addWidget(
            self.phase_range_panel
        )

        self.phase_range_panel.range_changed.connect(
            self.phase_range_changed
        )

        sidebar_layout.addWidget(
            self.parameter_panel
        )

        self.parameter_panel.parameter_changed.connect(
            self.parameter_changed
        )


        # -------------------------------------------------
        # Analysis section
        # -------------------------------------------------

        analysis_title = QLabel(
            "ANALYSIS"
        )

        analysis_title.setObjectName(
            "SectionTitle"
        )

        sidebar_layout.addSpacing(
            10
        )

        sidebar_layout.addWidget(
            analysis_title
        )


        self.analysis_button.setMinimumHeight(
            42
        )

        sidebar_layout.addWidget(
            self.analysis_button
        )
        # -------------------------------------------------
        # View controls
        # -------------------------------------------------

        sidebar_layout.addSpacing(
            12
        )

        view_title = QLabel(
            "VIEW"
        )

        view_title.setObjectName(
            "SectionTitle"
        )

        sidebar_layout.addWidget(
            view_title
        )


        self.show_function_checkbox = AnimatedSwitch(
            "Function plot  f(x)"
        )

        self.show_phase_checkbox = AnimatedSwitch(
            "Phase line"
        )

        self.show_time_checkbox = AnimatedSwitch(
            "Trajectory  x(t)"
        )


        self.show_function_checkbox.setChecked(
            True
        )

        self.show_phase_checkbox.setChecked(
            True
        )

        self.show_time_checkbox.setChecked(
            False
        )


        sidebar_layout.addWidget(
            self.show_function_checkbox
        )

        sidebar_layout.addWidget(
            self.show_phase_checkbox
        )

        sidebar_layout.addWidget(
            self.show_time_checkbox
        )


        self.show_function_checkbox.toggled.connect(
            self.update_view_visibility
        )

        self.show_phase_checkbox.toggled.connect(
            self.update_view_visibility
        )

        self.show_time_checkbox.toggled.connect(
            self.update_view_visibility
        )


        # -------------------------------------------------
        # Helpful sidebar text
        # -------------------------------------------------

        probe_hint = QLabel(
            "Move the pointer across the curve "
            "to inspect x, f(x), and f′(x)."
        )

        probe_hint.setObjectName(
            "SidebarHint"
        )

        probe_hint.setWordWrap(
            True
        )

        sidebar_layout.addSpacing(
            10
        )

        sidebar_layout.addWidget(
            probe_hint
        )


        # Push controls toward the top.
        sidebar_layout.addStretch()
        # =================================================
        # GRAPH
        # =================================================

        self.graph = pg.PlotWidget()

        self.graph.setBackground("#0d1424")

        self.graph.setLabel(
            "bottom",
            "x",
        )

        self.graph.setLabel(
            "left",
            "y",
        )

        self.graph.showGrid(
            x=True,
            y=True,
            alpha=0.12,
        )
# -------------------------------------------------
# Scientific axis styling
# -------------------------------------------------

        bottom_axis = self.graph.getAxis("bottom")
        left_axis = self.graph.getAxis("left")

        axis_pen = pg.mkPen(
            "#64748b",
            width=1,
        )

        axis_text_pen = pg.mkPen(
            "#94a3b8",
        )

        bottom_axis.setPen(axis_pen)
        left_axis.setPen(axis_pen)

        bottom_axis.setTextPen(axis_text_pen)
        left_axis.setTextPen(axis_text_pen)

        bottom_axis.setTickPen(axis_pen)
        left_axis.setTickPen(axis_pen)

        self.x_zero_axis = pg.InfiniteLine(
            pos=0,
            angle=0,
            movable=False,
            pen=pg.mkPen(
                "#475569",
                width=1.3,
            ),
        )

        self.y_zero_axis = pg.InfiniteLine(
            pos=0,
            angle=90,
            movable=False,
            pen=pg.mkPen(
                "#475569",
                width=1.3,
            ),
        )

        self.x_zero_axis.setZValue(-5)
        self.y_zero_axis.setZValue(-5)

        self.graph.addItem(
            self.x_zero_axis
        )

        self.graph.addItem(
            self.y_zero_axis
        )

        # Main function curve
        self.curve = pg.PlotDataItem(
            pen=pg.mkPen(
                "#38bdf8",
                width=3,
            )
        )       

        self.graph.addItem(
            self.curve
        )

        # =================================================
        # LIVE MATHEMATICAL PROBE
        # =================================================

        self.hover_marker = pg.ScatterPlotItem(
            size=11,
            symbol="o",
            pen=pg.mkPen(
            "#fef3c7",
            width=2,
            ),
            brush=pg.mkBrush(
            "#fbbf24"
            ),
        )

        self.graph.addItem(
            self.hover_marker
        )

        self.vertical_probe = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(
                "k",
                width=1,
                style=Qt.PenStyle.DotLine,
            ),
        )

        self.graph.addItem(
            self.vertical_probe
        )

        self.tangent_line = pg.PlotDataItem(
            pen=pg.mkPen(
                "#c084fc",
                width=2,
                style=Qt.PenStyle.DashLine,
            )
        )

        self.graph.addItem(
            self.tangent_line
        )

        self.hover_text = pg.TextItem(
            anchor=(0, 1),
            color="#f8fafc",
            fill=pg.mkBrush(
                15,
                23,
                42,
                235,
            ),
            border=pg.mkPen(
                "#38bdf8",
                width=1.5,
            ),
        )

        self.graph.addItem(
            self.hover_text
        )

        # =================================================
        # OPTIONAL ANALYSIS LAYERS
        # =================================================

        self.derivative_curve = pg.PlotDataItem(
            pen=pg.mkPen(
                "#34d399",
                width=2,
                style=Qt.PenStyle.DashLine,
            )
        )

        self.graph.addItem(
            self.derivative_curve
        )

        self.root_markers = pg.ScatterPlotItem(
            size=13,
            symbol="o",
            pen=pg.mkPen(
                "#fecaca",
                width=2,
            ),
            brush=pg.mkBrush(
                "#ef4444"
            ),
        )

        self.graph.addItem(
            self.root_markers
        )

        self.extrema_markers = pg.ScatterPlotItem(
            size=14,
            symbol="t",
            pen=pg.mkPen(
                "#cffafe",
                width=2,
            ),
            brush=pg.mkBrush(
                "#06b6d4"
            ),
        )

        self.graph.addItem(
            self.extrema_markers
        )

        # =================================================
        # RAW CLICK COORDINATE MARKER
        # =================================================

        self.coordinate_marker = pg.ScatterPlotItem(
            size=10,
            symbol="o",
            pen=pg.mkPen(
                "r",
                width=2,
            ),
            brush=pg.mkBrush("r"),
        )

        self.graph.addItem(
            self.coordinate_marker
        )

        # =================================================
        # STATUS AREA
        # =================================================

        self.coordinate_label = QLabel(
            "Click anywhere on the graph "
            "to inspect raw coordinates."
        )

        self.status_label = QLabel(
            "Ready"
        )

        # =================================================
        # MAIN LAYOUT
        # =================================================

        # =================================================
        # APPLICATION HEADER
        # =================================================

        header = QFrame()

        header.setObjectName(
            "HeaderBar"
        )

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            22,
            14,
            22,
            14,
        )


        title_area = QVBoxLayout()

        title_area.setSpacing(
            2
        )


        app_title = QLabel(
            "Dynamical Systems Lab"
        )

        app_title.setObjectName(
            "AppTitle"
        )


        app_subtitle = QLabel(
            "MANU’S LAB   /   Interactive mathematical laboratory"
        )

        app_subtitle.setObjectName(
            "AppSubtitle"
        )


        title_area.addWidget(
            app_title
        )

        title_area.addWidget(
            app_subtitle
        )


        header_layout.addLayout(
            title_area
        )

        header_layout.addStretch()


        workspace_badge = QLabel(
            "●  DYNAMICAL SYSTEMS"
        )

        workspace_badge.setObjectName(
            "WorkspaceBadge"
        )

        header_layout.addWidget(
            workspace_badge
        )


        # =================================================
        # GRAPH WORKSPACE CARD
        # =================================================

        graph_card = QFrame()

        graph_card.setObjectName(
            "GraphCard"
        )


        graph_layout = QVBoxLayout(
            graph_card
        )

        graph_layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        graph_layout.setSpacing(
            8
        )


        self.graph_title = QLabel(
            "Function Explorer"
        )

        self.graph_title.setObjectName(
            "CanvasTitle"
        )


        graph_layout.addWidget(
            self.graph_title
        )

        graph_layout.addWidget(
            self.graph
        )
        self.phase_title = QLabel(
            "Phase line"
        )

        self.phase_title.setObjectName(
            "CanvasTitle"
        )

        self.phase_line = PhaseLineWidget()

        graph_layout.addWidget(
            self.phase_title
        )

        graph_layout.addWidget(
            self.phase_line
        )
        self.time_series_title = QLabel(
            "Trajectory"
        )

        self.time_series_title.setObjectName(
            "CanvasTitle"
        )

        self.time_series = TimeSeriesWidget()

        graph_layout.addWidget(
            self.time_series_title
        )

        graph_layout.addWidget(
            self.time_series
        )
        self.simulation_config = (
            SimulationConfig(
                t_start=0.0,
                t_end=10.0,
                num_points=1200,
                method="RK45",
                rtol=1e-7,
                atol=1e-9,
            )
        )


        # =================================================
        # SPLIT WORKSPACE
        # =================================================

        workspace_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        workspace_splitter.setChildrenCollapsible(
            False
        )

        workspace_splitter.addWidget(
            self.left_panel
        )

        workspace_splitter.addWidget(
            graph_card
        )

        workspace_splitter.setStretchFactor(
            0,
            0,
        )

        workspace_splitter.setStretchFactor(
            1,
            1,
        )

        workspace_splitter.setSizes(
            [
                275,
                825,
            ]
        )


        # =================================================
        # BOTTOM INFORMATION STRIP
        # =================================================

        info_strip = QFrame()

        info_strip.setObjectName(
            "InfoStrip"
        )


        info_layout = QVBoxLayout(
            info_strip
        )

        info_layout.setContentsMargins(
            16,
            9,
            16,
            9,
        )

        info_layout.setSpacing(
            4
        )


        self.coordinate_label.setObjectName(
            "CoordinateReadout"
        )

        self.status_label.setObjectName(
            "StatusReadout"
        )


        info_layout.addWidget(
            self.coordinate_label
        )

        info_layout.addWidget(
            self.status_label
        )


        # =================================================
        # MAIN WINDOW LAYOUT
        # =================================================

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        main_layout.setSpacing(
            10
        )


        main_layout.addWidget(
            header
        )

        main_layout.addWidget(
            workspace_splitter,
            1,
        )

        main_layout.addWidget(
            info_strip
        )


        container = QWidget()

        container.setLayout(
            main_layout
        )

        self.setCentralWidget(
            container
        )

        # =================================================
        # CONNECTIONS
        # =================================================

        self.plot_button.clicked.connect(
            self.plot_expression
        )
        self.phase_line.initial_condition_selected.connect(
            self.run_1d_trajectory
        )

        self.equation_input.returnPressed.connect(
            self.plot_expression
        )

        self.graph.scene().sigMouseClicked.connect(
            self.graph_clicked
        )

        self.mouse_proxy = pg.SignalProxy(
            self.graph.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.mouse_moved,
        )

        self.derivative_curve_action.toggled.connect(
            lambda _: self.refresh_analysis()
        )

        self.roots_action.toggled.connect(
            lambda _: self.refresh_analysis()
        )

        self.extrema_action.toggled.connect(
            lambda _: self.refresh_analysis()
        )

        self.integral_action.triggered.connect(
            self.calculate_integral
        )

        self.clear_integral_action.triggered.connect(
            self.clear_integral
        )
        mount_presentation(self, header, graph_card, workspace_splitter)
        self.update_view_visibility()

        # Initial plot
        self.plot_expression()

    # =================================================
    # PLOT FUNCTION
    # =================================================

    def run_1d_trajectory(
        self,
        x0,
    ):

        if not self.current_expression:
            return

        try:

            trajectory = (
                integrate_1d_expression(
                    expression=(
                        self.current_expression
                    ),
                    x0=float(x0),
                    config=(
                        self.simulation_config
                    ),
                )
            )

            self.show_time_checkbox.setChecked(
                True
            )


            self.time_series.show_trajectory(
                trajectory
            )

            final_x = float(
                trajectory.y[
                    0,
                    -1,
                ]
            )

            self.status_label.setText(
                f"1D trajectory: "
                f"x₀ = {x0:.4f}  →  "
                f"x({trajectory.t[-1]:.2f}) "
                f"= {final_x:.6f}   "
                f"[{trajectory.method}]"
            )

        except Exception as error:

            self.status_label.setText(
                f"Trajectory error: {error}"
            )

    def update_view_visibility(
        self,
    ):

        show_function = (
            self.show_function_checkbox
            .isChecked()
        )

        show_phase = (
            self.show_phase_checkbox
            .isChecked()
        )

        show_time = (
            self.show_time_checkbox
            .isChecked()
        )

        if hasattr(self, "plot_cards"):
            for card, visible in zip(
                self.plot_cards, (show_function, show_phase, show_time)
            ):
                card.reveal(visible, animate=self.isVisible())
            if show_phase and self.isVisible():
                self.phase_line.animation_timer.start()
            else:
                self.phase_line.animation_timer.stop()
            return

        # Function plot
        self.graph_title.setVisible(
            show_function
        )

        self.graph.setVisible(
            show_function
        )

        # Phase line
        self.phase_title.setVisible(
            show_phase
        )

        self.phase_line.setVisible(
            show_phase
        )

        # Pause its animation when hidden
        if show_phase:

            if not (
                self.phase_line
                .animation_timer
                .isActive()
            ):

                self.phase_line.animation_timer.start()

        else:

            self.phase_line.animation_timer.stop()

        # Time-series trajectory
        self.time_series_title.setVisible(
            show_time
        )

        self.time_series.setVisible(
            show_time
        )





    def showEvent(self, event):
        super().showEvent(event)
        if self.show_phase_checkbox.isChecked():
            self.phase_line.animation_timer.start()

    def hideEvent(self, event):
        self.phase_line.animation_timer.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.phase_line.animation_timer.stop()
        super().closeEvent(event)

    def plot_expression(self):

        expression = (
            self.equation_input
            .text()
            .strip()
        )
        try:
            parameter_names = detect_parameters(expression)
        except ExpressionError as error:
            self.status_label.setText(f"Error: {error}")
            return

        self.parameter_panel.set_parameters(
            parameter_names
        )

        parameter_values = (
            self.parameter_panel.values()
        )

        resolved_expression = resolve_parameters(
            expression,
            parameter_values,
        )

        if not expression:

            self.status_label.setText(
                "Please enter an expression."
            )

            return

        x = np.linspace(
            -5,
            5,
            1500,
        )

        try:

            y = evaluate_expression(
                resolved_expression,
                x,
            )

            finite = np.isfinite(y)

            if not np.any(finite):

                raise ExpressionError(
                    "No finite values in this interval."
                )


            self.current_expression = resolved_expression

            phase_min, phase_max = (
                self.phase_range_panel.values()
            )

            self.phase_line.update_phase_line(
                resolved_expression,
                phase_min,
                phase_max,
            )

            self.plot_x = x
            self.plot_y = y

            self.curve.setData(
                x[finite],
                y[finite],
            )



            self.coordinate_marker.clear()

            self.clear_integral()

            self.hide_probe()

            self.refresh_analysis()

            self.coordinate_label.setText(
                "Click anywhere on the graph "
                "to inspect raw coordinates."
            )

            self.status_label.setText(
                f"Plotted: y = {expression}"
            )

        except ExpressionError as error:

            self.status_label.setText(
                f"Error: {error}"
            )

    # =================================================
    # LIVE HOVER PROBE
    # =================================================

    def mouse_moved(
        self,
        event,
    ):

        if not self.current_expression:
            return

        mouse_position = event[0]

        view_box = self.graph.getViewBox()

        if not (
            view_box
            .sceneBoundingRect()
            .contains(
                mouse_position
            )
        ):

            self.hide_probe()
            return

        graph_position = (
            view_box.mapSceneToView(
                mouse_position
            )
        )

        x_value = graph_position.x()

        try:

            y_value = function_value(
                self.current_expression,
                x_value,
            )

            derivative = numerical_derivative(
                self.current_expression,
                x_value,
            )

            if not (
                np.isfinite(y_value)
                and np.isfinite(derivative)
            ):

                self.hide_probe()
                return

            # -----------------------------------------
            # Snap marker to actual function
            # -----------------------------------------

            self.hover_marker.setData(
                [x_value],
                [y_value],
            )

            self.hover_marker.setVisible(True)

            # -----------------------------------------
            # Vertical guide
            # -----------------------------------------

            self.vertical_probe.setPos(
                x_value
            )

            self.vertical_probe.setVisible(
                True
            )

            # -----------------------------------------
            # Floating readout
            # ALWAYS keeps x, f(x), f'(x)
            # -----------------------------------------

            text = (
                f"x = {x_value:.4f}\n"
                f"f(x) = {y_value:.4f}\n"
                f"f′(x) = {derivative:.4f}"
            )

            if (
                self.second_derivative_action
                .isChecked()
            ):

                second = (
                    numerical_second_derivative(
                        self.current_expression,
                        x_value,
                    )
                )

                text += (
                    f"\nf″(x) = "
                    f"{second:.4f}"
                )

            self.hover_text.setText(
                text
            )

            x_range, y_range = (
                self.graph.viewRange()
            )

            width = (
                x_range[1]
                - x_range[0]
            )

            height = (
                y_range[1]
                - y_range[0]
            )

            self.hover_text.setPos(
                x_value + width * 0.02,
                y_value + height * 0.04,
            )

            self.hover_text.setVisible(
                True
            )

            # -----------------------------------------
            # Optional tangent line
            # -----------------------------------------

            if (
                self.tangent_action
                .isChecked()
            ):

                half_width = (
                    width * 0.10
                )

                tangent_x = np.array(
                    [
                        x_value - half_width,
                        x_value + half_width,
                    ]
                )

                tangent_y = (
                    y_value
                    + derivative
                    * (
                        tangent_x - x_value
                    )
                )

                self.tangent_line.setData(
                    tangent_x,
                    tangent_y,
                )

                self.tangent_line.setVisible(
                    True
                )

            else:

                self.tangent_line.setVisible(
                    False
                )

        except Exception:

            self.hide_probe()

    # =================================================
    # RAW CLICK COORDINATE
    # =================================================

    def graph_clicked(
        self,
        event,
    ):

        mouse_position = (
            event.scenePos()
        )

        view_box = (
            self.graph.getViewBox()
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
            view_box
            .mapSceneToView(
                mouse_position
            )
        )

        x_value = graph_position.x()
        y_value = graph_position.y()

        self.coordinate_marker.setData(
            [x_value],
            [y_value],
        )

        self.coordinate_label.setText(
            f"Clicked position: "
            f"x = {x_value:.4f}    "
            f"y = {y_value:.4f}"
        )

    # =================================================
    # OPTIONAL ANALYSIS
    # =================================================

    def refresh_analysis(
        self,
    ):

        if not self.current_expression:
            return

        self.clear_analysis_labels()

        # -----------------------------------------
        # Derivative curve
        # -----------------------------------------

        if (
            self.derivative_curve_action
            .isChecked()
        ):

            derivative = derivative_values(
                self.current_expression,
                self.plot_x,
            )

            finite = np.isfinite(
                derivative
            )

            self.derivative_curve.setData(
                self.plot_x[finite],
                derivative[finite],
            )

        else:

            self.derivative_curve.clear()

        # -----------------------------------------
        # Roots
        # -----------------------------------------

        if self.roots_action.isChecked():

            roots = find_roots(
                self.current_expression,
                float(self.plot_x[0]),
                float(self.plot_x[-1]),
            )

            root_y = np.zeros(
                len(roots)
            )

            self.root_markers.setData(
                roots,
                root_y,
            )

            for root in roots:

                label = pg.TextItem(
                    text=(
                        f"root\n"
                        f"x={root:.3f}"
                    ),
                    anchor=(0.5, 1.2),
                    color="r",
                )

                label.setPos(
                    root,
                    0,
                )

                self.graph.addItem(
                    label
                )

                self.analysis_labels.append(
                    label
                )

        else:

            self.root_markers.clear()

        # -----------------------------------------
        # Extrema
        # -----------------------------------------

        if self.extrema_action.isChecked():

            extrema = find_extrema(
                self.current_expression,
                float(self.plot_x[0]),
                float(self.plot_x[-1]),
            )

            x_values = [
                item["x"]
                for item in extrema
            ]

            y_values = [
                item["y"]
                for item in extrema
            ]

            self.extrema_markers.setData(
                x_values,
                y_values,
            )

            for item in extrema:

                label = pg.TextItem(
                    text=(
                        f"{item['kind']}\n"
                        f"x={item['x']:.3f}"
                    ),
                    anchor=(0.5, 1.2),
                    color="#d8e5ef",
                )

                label.setPos(
                    item["x"],
                    item["y"],
                )

                self.graph.addItem(
                    label
                )

                self.analysis_labels.append(
                    label
                )

        else:

            self.extrema_markers.clear()

    # =================================================
    # DEFINITE INTEGRAL
    # =================================================

    def calculate_integral(self):

        if not self.current_expression:
            return

        # -------------------------------------------------
        # Ask for integration limits
        # -------------------------------------------------

        a, ok = QInputDialog.getDouble(
            self,
            "Definite Integral",
            "Lower limit a:",
            -1.0,
            -100000,
            100000,
            4,
        )

        if not ok:
            return

        b, ok = QInputDialog.getDouble(
            self,
            "Definite Integral",
            "Upper limit b:",
            1.0,
            -100000,
            100000,
            4,
        )

        if not ok:
            return

        if a == b:

            self.status_label.setText(
                "Integral = 0 because a = b."
            )

            return

        try:

            # -------------------------------------------------
            # Calculate definite integral
            # -------------------------------------------------

            value, error = definite_integral(
                self.current_expression,
                a,
                b,
            )

            # Remove previous integral graphics
            self.clear_integral()

            # Always generate plotting points left -> right
            lower_x = min(a, b)
            upper_x = max(a, b)

            x_fill = np.linspace(
                lower_x,
                upper_x,
                800,
            )

            y_fill = evaluate_expression(
                self.current_expression,
                x_fill,
            )

            finite = np.isfinite(y_fill)

            if not np.all(finite):
                raise ValueError(
                    "The function is not finite throughout "
                    "the selected integration interval."
                )

            # =================================================
            # CURVE DEFINING TOP OF SHADED REGION
            # =================================================

            upper_curve = pg.PlotCurveItem(
                x=x_fill,
                y=y_fill,
                pen=pg.mkPen(
                    50,
                    100,
                    220,
                    width=2,
                ),
            )

            # =================================================
            # X-AXIS DEFINING BOTTOM OF SHADED REGION
            # =================================================

            zero_curve = pg.PlotCurveItem(
                x=x_fill,
                y=np.zeros_like(x_fill),
                pen=pg.mkPen(
                    100,
                    100,
                    100,
                    width=1,
                ),
            )

            # =================================================
            # ACTUAL SHADED REGION
            # =================================================

            fill = pg.FillBetweenItem(
                curve1=upper_curve,
                curve2=zero_curve,
                brush=pg.mkBrush(
                    34,
                    211,
                    238,
                    95,
                ),
            )

            # Put shading above graph background
            # but below most analysis markers.
            fill.setZValue(-1)

            upper_curve.setZValue(1)
            zero_curve.setZValue(0)

            self.graph.addItem(fill)
            self.graph.addItem(upper_curve)
            self.graph.addItem(zero_curve)

            # =================================================
            # INTEGRATION BOUNDARIES
            # =================================================

            left_boundary = pg.InfiniteLine(
                pos=a,
                angle=90,
                movable=False,
                pen=pg.mkPen(
                    70,
                    70,
                    70,
                    width=2,
                    style=Qt.PenStyle.DashLine,
                ),
            )

            right_boundary = pg.InfiniteLine(
                pos=b,
                angle=90,
                movable=False,
                pen=pg.mkPen(
                    70,
                    70,
                    70,
                    width=2,
                    style=Qt.PenStyle.DashLine,
                ),
            )

            left_boundary.setZValue(3)
            right_boundary.setZValue(3)

            self.graph.addItem(
                left_boundary
            )

            self.graph.addItem(
                right_boundary
            )

            # =================================================
            # CHOOSE GOOD POSITION FOR INTEGRAL LABEL
            # =================================================

            mid_x = (
                lower_x + upper_x
            ) / 2

            midpoint_value = function_value(
                self.current_expression,
                mid_x,
            )

            # Put label roughly halfway between
            # the x-axis and the function.
            label_y = midpoint_value / 2

            # If midpoint happens to be close to zero,
            # use the mean magnitude of the shaded curve.
            if abs(label_y) < 1e-8:

                mean_height = np.mean(
                    y_fill
                )

                label_y = mean_height / 2

            # =================================================
            # INTEGRAL VALUE INSIDE SHADED REGION
            # =================================================

            integral_label = pg.TextItem(
                text=(
                    f"∫ f(x) dx\n"
                    f"= {value:.6f}"
                ),
                anchor=(0.5, 0.5),
                color="#f8fafc",
                fill=pg.mkBrush(
                    15,
                    23,
                    42,
                    230,
                ),
                border=pg.mkPen(
                    "#22d3ee",
                    width=1.5,
                ),
            )

            integral_label.setPos(
                mid_x,
                label_y,
            )

            integral_label.setZValue(
                10
            )

            self.graph.addItem(
                integral_label
            )

            # =================================================
            # a AND b LABELS
            # =================================================

            y_range = (
                self.graph.viewRange()[1]
            )

            bottom_y = y_range[0]

            a_label = pg.TextItem(
                text=f"a = {a:.3f}",
                anchor=(0.5, 0),
                color="#d8e5ef",
                fill=pg.mkBrush(
                    255,
                    255,
                    255,
                    180,
                ),
            )

            b_label = pg.TextItem(
                text=f"b = {b:.3f}",
                anchor=(0.5, 0),
                color="#d8e5ef",
                fill=pg.mkBrush(
                    255,
                    255,
                    255,
                    180,
                ),
            )

            a_label.setPos(
                a,
                bottom_y
            )

            b_label.setPos(
                b,
                bottom_y
            )

            a_label.setZValue(10)
            b_label.setZValue(10)

            self.graph.addItem(
                a_label
            )

            self.graph.addItem(
                b_label
            )

            # =================================================
            # REMEMBER EVERYTHING FOR "CLEAR INTEGRAL"
            # =================================================

            self.integral_items = [
                fill,
                upper_curve,
                zero_curve,
                left_boundary,
                right_boundary,
                integral_label,
                a_label,
                b_label,
            ]

            # =================================================
            # STATUS
            # =================================================

            self.status_label.setText(
                f"Signed integral from "
                f"{a:.4f} to {b:.4f} "
                f"= {value:.6f}    "
                f"(estimated numerical error "
                f"{error:.2e})"
            )

        except Exception as error:

            self.status_label.setText(
                f"Integral error: {error}"
            )

    def clear_integral(
        self,
    ):

        for item in self.integral_items:

            try:

                self.graph.removeItem(
                    item
                )

            except Exception:
                pass

        self.integral_items = []
    def parameter_changed(
        self,
        name,
        value,
    ):

        self.plot_expression()

    def phase_range_changed(
        self,
        minimum,
        maximum,
    ):

        if not self.current_expression:
            return

        self.phase_line.update_phase_line(
            self.current_expression,
            minimum,
            maximum,
        )

    def clear_analysis_labels(
        self,
    ):

        for label in self.analysis_labels:

            try:

                self.graph.removeItem(
                    label
                )

            except Exception:
                pass

        self.analysis_labels = []

    def hide_probe(
        self,
    ):

        self.hover_marker.setVisible(
            False
        )

        self.vertical_probe.setVisible(
            False
        )

        self.tangent_line.setVisible(
            False
        )

        self.hover_text.setVisible(
            False
        )
