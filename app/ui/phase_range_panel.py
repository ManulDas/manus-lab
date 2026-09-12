from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class PhaseRangePanel(QWidget):

    range_changed = Signal(
        float,
        float,
    )

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

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
            6
        )

        title = QLabel(
            "PHASE LINE RANGE"
        )

        title.setObjectName(
            "SectionTitle"
        )

        self.main_layout.addWidget(
            title
        )

        controls = QHBoxLayout()

        # ---------------------------------------------
        # Minimum x
        # ---------------------------------------------

        min_label = QLabel(
            "Min x"
        )

        self.min_box = QDoubleSpinBox()

        self.min_box.setRange(
            -1_000_000.0,
            1_000_000.0,
        )

        self.min_box.setDecimals(
            3
        )

        self.min_box.setSingleStep(
            1.0
        )

        self.min_box.setValue(
            -5.0
        )

        # ---------------------------------------------
        # Maximum x
        # ---------------------------------------------

        max_label = QLabel(
            "Max x"
        )

        self.max_box = QDoubleSpinBox()

        self.max_box.setRange(
            -1_000_000.0,
            1_000_000.0,
        )

        self.max_box.setDecimals(
            3
        )

        self.max_box.setSingleStep(
            1.0
        )

        self.max_box.setValue(
            5.0
        )

        controls.addWidget(
            min_label
        )

        controls.addWidget(
            self.min_box
        )

        controls.addWidget(
            max_label
        )

        controls.addWidget(
            self.max_box
        )

        self.main_layout.addLayout(
            controls
        )

        # ---------------------------------------------
        # Connections
        # ---------------------------------------------

        self.min_box.valueChanged.connect(
            self._range_changed
        )

        self.max_box.valueChanged.connect(
            self._range_changed
        )

    def _range_changed(
        self,
    ):

        minimum = float(
            self.min_box.value()
        )

        maximum = float(
            self.max_box.value()
        )

        if minimum >= maximum:
            return

        self.range_changed.emit(
            minimum,
            maximum,
        )

    def values(
        self,
    ):

        return (
            float(
                self.min_box.value()
            ),
            float(
                self.max_box.value()
            ),
        )