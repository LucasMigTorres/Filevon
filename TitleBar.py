# Standard library imports
import os

# Third-party library imports
from PyQt6.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QToolButton,
    QWidget,
)


# Custom Title Bar class; Adapted from pythonguis.com/tutorials/custom-title-bar-pyqt6/
class TitleBar(QWidget):
    mousePressed = pyqtSignal(QPoint)

    # Constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos = None
        self.normal_geometry = None
        self._is_maximized = False
        self.icons = os.path.join(os.path.dirname(__file__), "icons")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        # Minimize button
        self.min_button = QToolButton(self)
        min_icon = QIcon(os.path.join(self.icons, "min.png"))
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Maximize button
        self.max_button = QToolButton(self)
        max_icon = QIcon(os.path.join(self.icons, "max.png"))
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.maximize_toggle)

        # Close button
        self.close_button = QToolButton(self)
        close_icon = QIcon(os.path.join(self.icons, "close.png"))
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        normal_icon = QIcon(os.path.join(self.icons, "normal.png"))
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.maximize_toggle)
        self.normal_button.setVisible(False)

        # List of buttons
        buttons = [self.min_button, self.normal_button, self.max_button, self.close_button]

        layout.addStretch()

        # Configure buttons
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            button.setStyleSheet("""
                QToolButton {
                    border: none;
                }
                """)
            layout.addWidget(button)

        # Call on_geometry_change upon available geometry change
        primary_screen = QGuiApplication.primaryScreen()
        primary_screen.availableGeometryChanged.connect(self.on_geometry_change)

    @property
    def is_maximized(self) -> bool:
        return self._is_maximized

    # Toggle maximize
    def maximize_toggle(self):
        win = self.window()
        screen = win.screen()
        if not screen:
            return

        if not self._is_maximized:
            # Save normal geometry
            self.normal_geometry = win.geometry()

            # Maximize
            rect = screen.availableGeometry()
            win.setGeometry(rect)

            self._is_maximized = True
            self.window_state_changed(Qt.WindowState.WindowMaximized)
        else:
            # Restore window
            if self.normal_geometry:
                win.setGeometry(self.normal_geometry)

            self._is_maximized = False
            self.window_state_changed(Qt.WindowState.WindowNoState)

        if hasattr(win, "apply_max_state"):
            win.apply_max_state(self._is_maximized)

    # Automatically adjust maximized window to screen
    def on_geometry_change(self):
        win = self.window()
        screen = win.screen()
        if not screen:
            return

        if self.is_maximized:
            # Change window geometry to fit screen
            rect = screen.availableGeometry()
            win.setGeometry(rect)
        else:
            return

    # Events to trigger upon window state change
    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

    # Detect left click on title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
            self.mousePressed.emit(event.globalPosition().toPoint())

        super().mousePressEvent(event)
        event.accept()

    # Drag window
    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            win = self.window()
            global_pos = event.globalPosition().toPoint()

            if self._is_maximized:
                # Preserve horizontal ratio before window restore
                x_ratio = self.initial_pos.x() / self.width()

                # Restore window
                self.maximize_toggle()

                # Convert ratio into restored window offset
                self.initial_pos = QPoint(
                    int(win.width() * x_ratio),
                    self.initial_pos.y()
                )

            win.move(
                global_pos.x() - self.initial_pos.x() - 10,
                global_pos.y() - self.initial_pos.y() - 10
            )

        super().mouseMoveEvent(event)
        event.accept()

    # Detect mouse release
    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()
