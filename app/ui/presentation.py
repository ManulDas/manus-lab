"""Reusable visual components. No numerical or application state lives here."""
from PySide6.QtCore import Qt, QRectF, QSize, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath
from PySide6.QtWidgets import (
    QCheckBox, QPushButton, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QWidget, QScrollArea, QGraphicsOpacityEffect,
)
import pyqtgraph as pg


ACCENT = "#65dfc3"
CANVAS = "#101c28"


class AnimatedButton(QPushButton):
    """Native button behavior with a brief, interruptible hover accent."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._hover = 0.0
        self._motion = QVariantAnimation(self)
        self._motion.setDuration(160)
        self._motion.setEasingCurve(QEasingCurve.OutCubic)
        self._motion.valueChanged.connect(self._frame)

    def _frame(self, value):
        self._hover = value
        self.update()

    def _animate(self, target):
        self._motion.stop()
        self._motion.setStartValue(self._hover)
        self._motion.setEndValue(target)
        self._motion.start()

    def enterEvent(self, event):
        self._animate(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate(0.0)
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(ACCENT)
        color.setAlphaF(0.45 * self._hover)
        painter.setPen(QPen(color, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 9, 9)


class AnimatedSwitch(QCheckBox):
    """QCheckBox semantics, keyboard access and signals with a sliding thumb."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)
        self._position = 0.0
        self._motion = QVariantAnimation(self)
        self._motion.setDuration(190)
        self._motion.setEasingCurve(QEasingCurve.OutCubic)
        self._motion.valueChanged.connect(self._frame)
        self.toggled.connect(self._toggle)

    def sizeHint(self):
        return QSize(self.fontMetrics().horizontalAdvance(self.text()) + 70, 38)

    def hitButton(self, point):
        return self.rect().contains(point)

    def _frame(self, value):
        self._position = value
        self.update()

    def _toggle(self, checked):
        self._motion.stop()
        self._motion.setStartValue(self._position)
        self._motion.setEndValue(float(checked))
        self._motion.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor("#d8e5ef" if self.isEnabled() else "#6c8192"))
        p.drawText(self.rect().adjusted(0, 0, -54, 0), Qt.AlignVCenter, self.text())
        x, y = self.width() - 42, (self.height() - 22) / 2
        t = self._position
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(int(43 + 58*t), int(61 + 162*t), int(78 + 117*t)))
        p.drawRoundedRect(QRectF(x, y, 40, 22), 11, 11)
        p.setBrush(QColor("#0c302c" if self.isChecked() else "#b2c4d3"))
        p.drawEllipse(QRectF(x + 3 + 18*t, y + 3, 16, 16))
        if self.hasFocus():
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(ACCENT), 1, Qt.DotLine))
            p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 6, 6)


class LabMark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#163b3b"))
        p.setPen(QPen(QColor("#285b54"), 1))
        p.drawRoundedRect(QRectF(1, 1, 46, 46), 14, 14)
        path = QPainterPath()
        path.moveTo(9, 30)
        path.cubicTo(16, 30, 13, 12, 22, 14)
        path.cubicTo(29, 16, 22, 36, 31, 34)
        path.cubicTo(36, 33, 35, 21, 40, 20)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(ACCENT), 2.2))
        p.drawPath(path)


class CurveEntrance:
    """Fade newly computed curves without changing samples or plot ranges."""
    def __init__(self, curve, parent):
        self.curve = curve
        self.motion = QVariantAnimation(parent)
        self.motion.setDuration(260)
        self.motion.setEasingCurve(QEasingCurve.OutCubic)
        self.motion.valueChanged.connect(curve.setOpacity)
        curve.sigPlotChanged.connect(self.start)

    def start(self, *args):
        running = self.motion.state() == QVariantAnimation.Running
        self.motion.stop()
        self.motion.setStartValue(self.curve.opacity() if running else 0.45)
        self.motion.setEndValue(1.0)
        self.motion.start()


class PlotCard(QFrame):
    def __init__(self, title, plot, number, subtitle, accent, parent=None):
        super().__init__(parent)
        self.setObjectName("PlotCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 12)
        layout.setSpacing(10)
        row = QHBoxLayout()
        index = QLabel(number)
        index.setObjectName("CardIndex")
        index.setStyleSheet(f"color: {accent}; background: transparent;")
        row.addWidget(index)
        row.addWidget(title)
        row.addStretch()
        hint = QLabel(subtitle)
        hint.setObjectName("CardHint")
        row.addWidget(hint)
        layout.addLayout(row)
        layout.addWidget(plot, 1)
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(1)
        self.setGraphicsEffect(self._effect)
        self._motion = QVariantAnimation(self)
        self._motion.setDuration(180)
        self._motion.setEasingCurve(QEasingCurve.OutCubic)
        self._motion.valueChanged.connect(self._effect.setOpacity)
        self._motion.finished.connect(self._finish)
        self._target = True

    def reveal(self, visible, animate=True):
        if self._target == visible and not self.isHidden():
            return
        self._target = visible
        self._motion.stop()
        if not animate:
            self._effect.setOpacity(1.0 if visible else 0.0)
            self.setVisible(visible)
            return
        if visible:
            self.show()
        self._motion.setStartValue(self._effect.opacity())
        self._motion.setEndValue(1.0 if visible else 0.0)
        self._motion.start()

    def _finish(self):
        self.setVisible(self._target)


def style_plot(plot):
    plot.setBackground(CANVAS)
    plot.setFrameShape(QFrame.NoFrame)
    for name in ("bottom", "left"):
        axis = plot.getAxis(name)
        axis.setPen(pg.mkPen("#304354"))
        axis.setTickPen(pg.mkPen("#304354"))
        axis.setTextPen(pg.mkPen("#8198aa"))
    plot.getPlotItem().setContentsMargins(2, 2, 8, 2)


def mount_presentation(window, header, graph_card, splitter):
    """Compose existing controls into cards without replacing their connections."""
    header.layout().insertWidget(0, LabMark(), 0, Qt.AlignVCenter)
    header.layout().setSpacing(16)
    window.left_panel.setMinimumWidth(300)
    window.left_panel.setMaximumWidth(360)
    scroll = QScrollArea()
    scroll.setObjectName("ControlScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setMinimumWidth(314)
    scroll.setMaximumWidth(374)
    scroll.setWidget(window.left_panel)
    splitter.insertWidget(0, scroll)
    splitter.setHandleWidth(14)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)
    splitter.setSizes([320, 960])

    layout = graph_card.layout()
    while layout.count():
        layout.takeAt(0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)
    window.plot_cards = []
    specs = (
        (window.graph_title, window.graph, "01", "f(x)  /  FUNCTION", ACCENT),
        (window.phase_title, window.phase_line, "02", "dx/dt = f(x)", "#b49cfa"),
        (window.time_series_title, window.time_series, "03", "x(t)  /  TRAJECTORY", "#f1c681"),
    )
    for title, plot, number, hint, accent in specs:
        style_plot(plot)
        card = PlotCard(title, plot, number, hint, accent)
        layout.addWidget(card, 0 if plot is window.phase_line else 1)
        window.plot_cards.append(card)
    window.graph.setMinimumHeight(110)
    window.time_series.setMinimumHeight(110)
    window.phase_line.setMinimumHeight(110)
    window.phase_line.setMaximumHeight(160)
    window.curve.setPen(pg.mkPen(ACCENT, width=2.6))
    window.vertical_probe.setPen(pg.mkPen("#6c8797", style=Qt.DotLine))
    window.time_series.trajectory_curve.setPen(pg.mkPen("#f1c681", width=2.4))
    window.plot_button.setObjectName("PrimaryButton")
    window.plot_button.setText("Plot function  →")
    window.equation_input.setObjectName("EquationInput")
    for widget in (window.plot_button, window.equation_input):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
    window.curve_entrances = [
        CurveEntrance(window.curve, window),
        CurveEntrance(window.time_series.trajectory_curve, window),
    ]
    window.coordinate_label.setWordWrap(True)
    window.status_label.setWordWrap(True)
    window.resize(1280, 880)
    window.setMinimumSize(960, 740)
