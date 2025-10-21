from PyQt6.QtCore import (Qt, QRect, QPropertyAnimation,
                          QEasingCurve, QEvent)
from PyQt6.QtWidgets import (QFrame, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QHBoxLayout)

from custom_widgets.separator import h_line

class SlideOverPanel(QFrame):
    def __init__(self, parent=None, width=280):
        super().__init__(parent)
        self._panel_width = width
        self.setObjectName("sidePanel")
        self.setFixedWidth(self._panel_width)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.separator_top = h_line()
        self.separator_bottom = h_line()
        self.separator_bottom.setObjectName("separatorBottom")
        # Content
        menu_layout = QVBoxLayout(self)
        menu_layout.setContentsMargins(16, 16, 16, 16)
        menu_layout.setSpacing(12)

        title_layout = QHBoxLayout()

        title = QLabel("Options")
        title.setObjectName("sidePanelTitle")

        menu_button = QPushButton("☰")
        menu_button.clicked.connect(self.toggle)
        menu_button.setObjectName("sidePanelButton")

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(menu_button)
        menu_layout.addLayout(title_layout)

        self.preferences_button = QPushButton("Saved Strings")
        self.preferences_button.setObjectName("sidePanelButton")



        self.help_button = QPushButton("Help")
        self.help_button.setObjectName("sidePanelButton")

        menu_layout.addWidget(self.separator_top)
        menu_layout.addWidget(self.preferences_button)
        menu_layout.addStretch(1)
        menu_layout.addStretch()
        menu_layout.addWidget(self.separator_bottom)
        menu_layout.addWidget(self.help_button)

        # Scrim overlay to catch outside clicks
        self._overlay = QWidget(self.window())
        self._overlay.setObjectName("scrimOverlay")
        self._overlay.hide()
        self._overlay.installEventFilter(self)

        # Anim
        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hide()

    # --- public API ---
    def toggle(self):
        if self.isVisible():
            self.closePanel()
        else:
            self.openPanel()

    def openPanel(self):
        p = self.parentWidget()
        if not p:
            return
        self._positionOverlay()
        self._overlay.show()
        self.show()


        self._overlay.raise_()
        self.raise_()

        start = QRect(p.width(), 0, self._panel_width, p.height())
        end = QRect(p.width() - self._panel_width, 0, self._panel_width, p.height())
        self.setGeometry(start)
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def closePanel(self):
        p = self.parentWidget()
        if not p:
            return
        start = QRect(self.geometry())
        end   = QRect(p.width(), 0, self._panel_width, p.height())
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.finished.connect(self._afterCloseOnce)
        self._anim.start()

    def _afterCloseOnce(self):
        try:
            self._anim.finished.disconnect(self._afterCloseOnce)
        except Exception:
            pass
        self.hide()
        self._overlay.hide()

    # Keep aligned on parent resize
    def resizeWithParent(self):
        p = self.parentWidget()
        if not p:
            return
        self._positionOverlay()
        if self.isVisible():
            self.setGeometry(p.width() - self._panel_width, 0, self._panel_width, p.height())

    def _positionOverlay(self):
        p = self.parentWidget()
        if p:
            self._overlay.setGeometry(0, 0, p.width(), p.height())

    def eventFilter(self, obj, ev):
        if obj is self._overlay and ev.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
            self.closePanel()
            return True
        return super().eventFilter(obj, ev)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.closePanel()
        else:
            super().keyPressEvent(e)
