import pyqtgraph as pg


class TimeSeriesWidget(
    pg.PlotWidget
):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent=parent
        )

        self.setBackground(
            "#0d1424"
        )

        self.setMinimumHeight(
            190
        )

        self.setLabel(
            "bottom",
            "t",
        )

        self.setLabel(
            "left",
            "x(t)",
        )

        self.showGrid(
            x=True,
            y=True,
            alpha=0.12,
        )

        # ---------------------------------------------
        # Axis appearance
        # ---------------------------------------------

        axis_pen = pg.mkPen(
            "#64748b",
            width=1,
        )

        axis_text_pen = pg.mkPen(
            "#94a3b8",
        )

        bottom_axis = self.getAxis(
            "bottom"
        )

        left_axis = self.getAxis(
            "left"
        )

        bottom_axis.setPen(
            axis_pen
        )

        left_axis.setPen(
            axis_pen
        )

        bottom_axis.setTextPen(
            axis_text_pen
        )

        left_axis.setTextPen(
            axis_text_pen
        )

        # ---------------------------------------------
        # x(t) trajectory
        # ---------------------------------------------

        self.trajectory_curve = (
            pg.PlotDataItem(
                pen=pg.mkPen(
                    "#38bdf8",
                    width=2.5,
                )
            )
        )

        self.addItem(
            self.trajectory_curve
        )

        # ---------------------------------------------
        # Initial-condition marker
        # ---------------------------------------------

        self.initial_marker = (
            pg.ScatterPlotItem(
                size=12,
                symbol="o",
                pen=pg.mkPen(
                    "#ffffff",
                    width=2,
                ),
                brush=pg.mkBrush(
                    "#fbbf24"
                ),
            )
        )

        self.addItem(
            self.initial_marker
        )

        # ---------------------------------------------
        # Final-state marker
        # ---------------------------------------------

        self.final_marker = (
            pg.ScatterPlotItem(
                size=11,
                symbol="o",
                pen=pg.mkPen(
                    "#d1fae5",
                    width=2,
                ),
                brush=pg.mkBrush(
                    "#34d399"
                ),
            )
        )

        self.addItem(
            self.final_marker
        )

    # =================================================
    # DISPLAY TRAJECTORY
    # =================================================

    def show_trajectory(
        self,
        trajectory,
    ):

        t = trajectory.t

        x = trajectory.y[
            0
        ]

        self.trajectory_curve.setData(
            t,
            x,
        )

        self.initial_marker.setData(
            [
                t[0]
            ],
            [
                x[0]
            ],
        )

        self.final_marker.setData(
            [
                t[-1]
            ],
            [
                x[-1]
            ],
        )

        self.enableAutoRange()

    def clear_trajectory(
        self,
    ):

        self.trajectory_curve.clear()
        self.initial_marker.clear()
        self.final_marker.clear()