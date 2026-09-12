from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ParameterPanel(QWidget):

    parameter_changed = Signal(
        str,
        float,
    )

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.parameter_names = []
        self.controls = {}

        self.main_layout = QVBoxLayout(
            self
        )

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.main_layout.setSpacing(
            14
        )

        self.setVisible(
            False
        )

    # =====================================================
    # SET PARAMETERS
    # =====================================================

    def set_parameters(
        self,
        names,
    ):

        names = list(
            names
        )

        # Preserve controls when the same parameters
        # remain in the expression.
        if names == self.parameter_names:
            return

        old_values = self.values()

        self.clear()

        self.parameter_names = names

        if not names:

            self.setVisible(
                False
            )

            return

        self.setVisible(
            True
        )

        for name in names:

            self._add_parameter(
                name,
                old_values.get(
                    name,
                    1.0,
                ),
            )

    # =====================================================
    # CREATE PARAMETER CONTROL
    # =====================================================

    def _add_parameter(
        self,
        name,
        initial_value,
    ):

        parameter_layout = QVBoxLayout()

        parameter_layout.setSpacing(
            6
        )

        # -------------------------------------------------
        # Parameter name
        # -------------------------------------------------

        name_label = QLabel(
            name
        )

        name_label.setStyleSheet(
            """
            font-weight: 700;
            font-size: 15px;
            color: #e2e8f0;
            """
        )

        parameter_layout.addWidget(
            name_label
        )

        # -------------------------------------------------
        # Min / Value / Max row
        # -------------------------------------------------

        controls_row = QHBoxLayout()

        controls_row.setSpacing(
            6
        )

        min_label = QLabel(
            "Min"
        )

        min_box = QDoubleSpinBox()

        min_box.setRange(
            -1_000_000.0,
            1_000_000.0,
        )

        min_box.setDecimals(
            3
        )

        min_box.setValue(
            -5.0
        )

        min_box.setSingleStep(
            0.5
        )

        value_label = QLabel(
            "Value"
        )

        value_box = QDoubleSpinBox()

        # Value entry is deliberately much wider
        # than the current slider bounds.
        value_box.setRange(
            -1_000_000.0,
            1_000_000.0,
        )

        value_box.setDecimals(
            4
        )

        value_box.setSingleStep(
            0.1
        )

        value_box.setValue(
            initial_value
        )

        max_label = QLabel(
            "Max"
        )

        max_box = QDoubleSpinBox()

        max_box.setRange(
            -1_000_000.0,
            1_000_000.0,
        )

        max_box.setDecimals(
            3
        )

        max_box.setValue(
            5.0
        )

        max_box.setSingleStep(
            0.5
        )

        # Keep every existing entry, with captions above to avoid clipping.
        for label, box in (
            (min_label, min_box), (value_label, value_box), (max_label, max_box)
        ):
            column = QVBoxLayout()
            column.setSpacing(5)
            label.setObjectName("SidebarHint")
            box.setMinimumWidth(0)
            column.addWidget(label)
            column.addWidget(box)
            controls_row.addLayout(column, 1)

        parameter_layout.addLayout(
            controls_row
        )

        # -------------------------------------------------
        # Slider
        # -------------------------------------------------

        slider = QSlider(
            Qt.Orientation.Horizontal
        )

        slider.setRange(
            0,
            1000,
        )

        slider.setValue(
            self._value_to_slider(
                initial_value,
                -5.0,
                5.0,
            )
        )

        parameter_layout.addWidget(
            slider
        )

        self.main_layout.addLayout(
            parameter_layout
        )

        # -------------------------------------------------
        # Store controls
        # -------------------------------------------------

        self.controls[
            name
        ] = {
            "slider": slider,
            "spinbox": value_box,
            "min_box": min_box,
            "max_box": max_box,
        }

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        slider.valueChanged.connect(
            lambda slider_value,
            parameter=name:
            self._slider_changed(
                parameter,
                slider_value,
            )
        )

        value_box.valueChanged.connect(
            lambda value,
            parameter=name:
            self._spinbox_changed(
                parameter,
                value,
            )
        )

        min_box.valueChanged.connect(
            lambda _,
            parameter=name:
            self._bounds_changed(
                parameter
            )
        )

        max_box.valueChanged.connect(
            lambda _,
            parameter=name:
            self._bounds_changed(
                parameter
            )
        )

    # =====================================================
    # SLIDER CHANGED
    # =====================================================

    def _slider_changed(
        self,
        name,
        slider_value,
    ):

        controls = self.controls[
            name
        ]

        minimum = float(
            controls[
                "min_box"
            ].value()
        )

        maximum = float(
            controls[
                "max_box"
            ].value()
        )

        value = (
            self._slider_to_value(
                slider_value,
                minimum,
                maximum,
            )
        )

        spinbox = controls[
            "spinbox"
        ]

        spinbox.blockSignals(
            True
        )

        spinbox.setValue(
            value
        )

        spinbox.blockSignals(
            False
        )

        self.parameter_changed.emit(
            name,
            value,
        )

    # =====================================================
    # VALUE BOX CHANGED
    # =====================================================

    def _spinbox_changed(
        self,
        name,
        value,
    ):

        controls = self.controls[
            name
        ]

        minimum = float(
            controls[
                "min_box"
            ].value()
        )

        maximum = float(
            controls[
                "max_box"
            ].value()
        )

        # If typed value is outside slider range,
        # automatically expand the corresponding bound.
        if value < minimum:

            controls[
                "min_box"
            ].blockSignals(
                True
            )

            controls[
                "min_box"
            ].setValue(
                value
            )

            controls[
                "min_box"
            ].blockSignals(
                False
            )

            minimum = value

        if value > maximum:

            controls[
                "max_box"
            ].blockSignals(
                True
            )

            controls[
                "max_box"
            ].setValue(
                value
            )

            controls[
                "max_box"
            ].blockSignals(
                False
            )

            maximum = value

        slider = controls[
            "slider"
        ]

        slider.blockSignals(
            True
        )

        slider.setValue(
            self._value_to_slider(
                value,
                minimum,
                maximum,
            )
        )

        slider.blockSignals(
            False
        )

        self.parameter_changed.emit(
            name,
            float(value),
        )

    # =====================================================
    # BOUNDS CHANGED
    # =====================================================

    def _bounds_changed(
        self,
        name,
    ):

        controls = self.controls[
            name
        ]

        minimum = float(
            controls[
                "min_box"
            ].value()
        )

        maximum = float(
            controls[
                "max_box"
            ].value()
        )

        # Prevent invalid slider interval.
        if minimum >= maximum:

            return

        value = float(
            controls[
                "spinbox"
            ].value()
        )

        # Clamp value into the newly chosen range.
        value = max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

        controls[
            "spinbox"
        ].blockSignals(
            True
        )

        controls[
            "spinbox"
        ].setValue(
            value
        )

        controls[
            "spinbox"
        ].blockSignals(
            False
        )

        controls[
            "slider"
        ].blockSignals(
            True
        )

        controls[
            "slider"
        ].setValue(
            self._value_to_slider(
                value,
                minimum,
                maximum,
            )
        )

        controls[
            "slider"
        ].blockSignals(
            False
        )

        self.parameter_changed.emit(
            name,
            value,
        )

    # =====================================================
    # CONVERSION BETWEEN VALUE AND SLIDER POSITION
    # =====================================================

    def _slider_to_value(
        self,
        slider_value,
        minimum,
        maximum,
    ):

        if maximum <= minimum:
            return minimum

        fraction = (
            slider_value
            / 1000
        )

        return (
            minimum
            + fraction
            * (
                maximum
                - minimum
            )
        )

    def _value_to_slider(
        self,
        value,
        minimum,
        maximum,
    ):

        if maximum <= minimum:
            return 0

        value = max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

        fraction = (
            value
            - minimum
        ) / (
            maximum
            - minimum
        )

        return int(
            round(
                fraction
                * 1000
            )
        )

    # =====================================================
    # RETURN PARAMETER VALUES
    # =====================================================

    def values(
        self,
    ):

        result = {}

        for (
            name,
            widgets,
        ) in self.controls.items():

            result[
                name
            ] = float(
                widgets[
                    "spinbox"
                ].value()
            )

        return result

    # =====================================================
    # CLEAR PANEL
    # =====================================================

    def clear(
        self,
    ):

        while (
            self.main_layout.count()
        ):

            item = (
                self.main_layout
                .takeAt(0)
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

            child_layout = (
                item.layout()
            )

            if child_layout is not None:

                self._clear_layout(
                    child_layout
                )

        self.controls = {}

    def _clear_layout(
        self,
        layout,
    ):

        while (
            layout.count()
        ):

            item = (
                layout.takeAt(0)
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

            child_layout = (
                item.layout()
            )

            if child_layout is not None:

                self._clear_layout(
                    child_layout
                )
