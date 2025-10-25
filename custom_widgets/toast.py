from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QFontMetrics
from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect, QSizePolicy


class Toast(QLabel):
    """Class for toast notifications."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 14px;
                font-family: "Calibri", sans-serif;
            }
        """)
        self._bg_color = QColor(30, 30, 30, 180)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.default_width = 300
        self.general_width = 120

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setVisible(False)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.fade_timer = QTimer()
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.fade_out)

        self.locations = {
            'top-selected': lambda x, y: (x, y - 280),
            'bottom-selected': lambda x, y: (x, y - 115),
            'left-selected': lambda x, y: (x - 300, y - 200),
            'right-selected': lambda x, y: (x + 300, y - 200),
            'chars-error': lambda x, y: (x + 48, y + 19),
            'general': lambda x, y: (x + 308, y),
        }

        self.colors = {
            'default': (30, 30, 30, 180),
            'error': (220, 50, 47, 40),
            'success': (50, 200, 100, 20),
            'warning': (255, 165, 0, 65),
            'info': (80, 160, 255, 50),
        }


    def show_toast(self, msg: str, duration: int = 2000,
                   location: str = None, theme: str = 'default'):

        if location not in self.locations:
            location = 'top-selected'
        theme = theme.lower() if isinstance(theme, str) else 'default'
        rgba = self.colors.get(theme, self.colors['default'])
        self._bg_color = QColor(*rgba)

        self.fade_animation.stop()
        self.fade_timer.stop()
        if self.fade_animation.receivers(self.fade_animation.finished):
            self.fade_animation.finished.disconnect()

        width = self.general_width if location == 'general' else self.default_width
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(msg, Qt.TextElideMode.ElideNone, width)
        wrapped = self._wrap_text(elided, metrics, width)
        self.setText(wrapped)

        self.setFixedWidth(width)
        self.adjustSize()
        self.opacity_effect.setOpacity(0.0)

        parent = self.parent()
        if parent:
            pos = parent.mapToGlobal(parent.rect().center())
            x = int(pos.x() - self.width() / 2)
            y = int(pos.y() - self.height() / 2)

            adjust_fn = self.locations.get(location)
            if callable(adjust_fn):
                x, y = adjust_fn(x, y)

            self.move(int(x), int(y))

        self.setVisible(True)
        self.raise_()

        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

        self.fade_timer.start(duration)


    def fade_out(self):
        self.fade_animation.stop()
        self.fade_animation.setDuration(400)
        self.fade_animation.setStartValue(self.opacity_effect.opacity())
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()
        self.fade_animation.finished.connect(lambda: self.setVisible(False))


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

    def _wrap_text(self, text, metrics, width):
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            if metrics.horizontalAdvance(test) > width - 20:  # padding allowance
                lines.append(line)
                line = word
            else:
                line = test
        lines.append(line)
        return "\n".join(lines)

