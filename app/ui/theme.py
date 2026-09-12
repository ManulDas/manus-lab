"""Shared application theme. Plot colors and reusable motion live in presentation.py."""
APP_STYLE = """
QWidget { color: #d8e5ef; font-family: "Helvetica Neue"; font-size: 13px; background: #0b131d; }
QLabel { background: transparent; }
QFrame#HeaderBar { background: #0b131d; border: none; }
QLabel#AppTitle { color: #f1f6fa; font-size: 25px; font-weight: 700; }
QLabel#AppSubtitle { color: #8198aa; font-size: 12px; }
QLabel#WorkspaceBadge { color: #65dfc3; background: #15312f; border: 1px solid #285149; border-radius: 12px; padding: 7px 14px; font-size: 11px; font-weight: 600; }
QFrame#Sidebar { background: #101c28; border: 1px solid #263747; border-radius: 14px; }
QFrame#Sidebar QWidget { background: transparent; }
QFrame#GraphCard { background: transparent; border: none; }
QFrame#PlotCard { background: #101c28; border: 1px solid #263747; border-radius: 14px; }
QLabel#CanvasTitle { color: #e2edf5; font-size: 14px; font-weight: 600; }
QLabel#CardIndex { font-family: "Menlo"; font-size: 12px; padding-right: 4px; }
QLabel#CardHint { color: #7d94a6; font-size: 10px; }
QLabel#SectionTitle { color: #8ca4b7; font-size: 10px; font-weight: 700; }
QLabel#SidebarHint { color: #8198aa; font-size: 12px; }
QLineEdit, QDoubleSpinBox, QFrame#Sidebar QDoubleSpinBox, QFrame#Sidebar QLineEdit {
 background: #0c1621; color: #e2edf5; border: 1px solid #314556; border-radius: 7px; padding: 7px 8px; selection-background-color: #285f59;
}
QLineEdit#EquationInput { font-family: "Menlo"; font-size: 14px; padding: 11px 9px; }
QLineEdit:focus, QDoubleSpinBox:focus { border: 1px solid #65dfc3; }
QLineEdit:hover, QDoubleSpinBox:hover { border: 1px solid #608277; }
QDoubleSpinBox { min-width: 45px; }
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 14px; border: none; }
QPushButton, QFrame#Sidebar QPushButton {
 background: #1b2d3c; border: 1px solid #365063; border-radius: 9px; padding: 9px 13px; color: #dce9f3; font-weight: 600;
}
QPushButton:pressed { background: #122331; }
QPushButton:focus { border: 1px solid #65dfc3; }
QPushButton#PrimaryButton, QFrame#Sidebar QPushButton#PrimaryButton { background: #65dfc3; border: 1px solid #65dfc3; color: #092b28; }
QPushButton#PrimaryButton:pressed { background: #43bea3; }
QPushButton::menu-indicator { subcontrol-position: right center; right: 12px; }
QSlider::groove:horizontal { height: 4px; background: #293e4f; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #65dfc3; border-radius: 2px; }
QSlider::handle:horizontal { background: #d5fff4; border: 3px solid #65dfc3; width: 10px; height: 10px; margin: -6px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { border-color: #a7f6e3; }
QFrame#InfoStrip { background: #101c28; border: 1px solid #263747; border-radius: 10px; }
QLabel#CoordinateReadout { color: #9bb0c0; font-family: "Menlo"; font-size: 11px; }
QLabel#StatusReadout { color: #65dfc3; font-size: 11px; }
QScrollArea#ControlScroll { background: transparent; border: none; }
QScrollBar:vertical { background: #0b131d; width: 7px; margin: 2px; }
QScrollBar::handle:vertical { background: #355062; min-height: 28px; border-radius: 3px; }
QScrollBar::handle:vertical:hover { background: #5c807e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QSplitter::handle { background: transparent; width: 14px; }
QMenu { background: #142331; border: 1px solid #365063; padding: 7px; }
QMenu::item { padding: 9px 30px 9px 14px; border-radius: 5px; }
QMenu::item:selected { background: #25463f; color: #bcffec; }
QMenu::separator { height: 1px; background: #304454; margin: 6px; }
QToolTip { background: #1a3040; color: #e2edf5; border: 1px solid #426052; padding: 7px; }
QDialog { background: #101c28; }
"""
