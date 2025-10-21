from PyQt6.QtCore import Qt, QPoint, pyqtSlot, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtGui import QPainter, QColor

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

class SwitchCircle(QWidget):
    def __init__(self, parent, move_range: tuple, color, animation_curve, animation_duration):
        super().__init__(parent=parent)
        self.move_range = move_range
        self.color = color
        self.setFixedSize(22, 22)  # important

        self.animation = QPropertyAnimation(self, b"pos", self)
        self.animation.setDuration(animation_duration)
        self.animation.setEasingCurve(animation_curve)

        self._press_x = 0
        self._new_x = self.x()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.color))
        painter.drawEllipse(0, 0, self.width(), self.height())

    def set_color(self, value):
        self.color = value
        self.update()

    def mousePressEvent(self, event):
        self.animation.stop()
        self._press_x = event.position().x()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        delta = event.position().x() - self._press_x
        self._new_x = clamp(self.x() + int(delta), self.move_range[0], self.move_range[1])
        self.move(self._new_x, self.y())
        self._press_x = event.position().x()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Snap to nearest end
        left, right = self.move_range
        go_right = abs(self.x() - right) < abs(self.x() - left)

        # Let parent own state; animation will be handled by parent via `toggled`
        parent = self.parent()
        if isinstance(parent, QCheckBox):
            parent.setChecked(go_right)

        super().mouseReleaseEvent(event)


class SwitchControl(QCheckBox):
    def __init__(
        self, parent=None,
        bg_color="#777777",
        circle_color="#DDDDDD",
        active_color="#aa00ff",
        animation_curve=QEasingCurve.OutBounce,
        animation_duration=500,
        checked: bool = False,
        change_cursor=True
    ):
        super().__init__(parent=parent)

        # You can change this size; geometry scales automatically now.
        self.setFixedSize(60, 28)

        if change_cursor:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color
        self._anim_curve = animation_curve
        self._anim_duration = animation_duration

        thumb_margin = 3
        thumb_d = self.height() - 2 * thumb_margin  # 22 by default
        left_x = thumb_margin
        right_x = self.width() - thumb_margin - thumb_d

        self._thumb = SwitchCircle(
            self,
            move_range=(left_x, right_x),
            color=self._circle_color,
            animation_curve=self._anim_curve,
            animation_duration=self._anim_duration,
        )
        self._thumb.move(right_x if checked else left_x, thumb_margin)
        self.setChecked(checked)

        # Single animation path, driven by state
        self._anim = QPropertyAnimation(self._thumb, b"pos", self)
        self._anim.setDuration(animation_duration)
        self._anim.setEasingCurve(animation_curve)

        # Animate on any state change (mouse, keyboard, programmatic)
        self.toggled.connect(self.start_animation)

        self._auto_click = False
        self._press_global = None

    # ------- Properties -------
    def get_bg_color(self): return self._bg_color
    @pyqtSlot(str)
    def set_bg_color(self, v): self._bg_color = v; self.update()
    backgroundColor = pyqtProperty(str, get_bg_color, set_bg_color)

    def get_circle_color(self): return self._circle_color
    @pyqtSlot(str)
    def set_circle_color(self, v): self._circle_color = v; self._thumb.set_color(v); self.update()
    circleBackgroundColor = pyqtProperty(str, get_circle_color, set_circle_color)

    def get_active_color(self): return self._active_color
    @pyqtSlot(str)
    def set_active_color(self, v): self._active_color = v; self.update()
    activeColor = pyqtProperty(str, get_active_color, set_active_color)

    def get_animation_duration(self): return self._anim_duration
    @pyqtSlot(int)
    def set_animation_duration(self, v):
        self._anim_duration = v
        self._anim.setDuration(v)
    animationDuration = pyqtProperty(int, get_animation_duration, set_animation_duration)

    # ------- Behavior -------
    def start_animation(self, checked: bool):
        thumb_margin = 3
        thumb_d = self.height() - 2 * thumb_margin
        left_x = thumb_margin
        right_x = self.width() - thumb_margin - thumb_d

        self._anim.stop()
        self._anim.setStartValue(self._thumb.pos())
        end_x = right_x if checked else left_x
        self._anim.setEndValue(QPoint(end_x, self._thumb.y()))
        self._anim.start()
        self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        color = self._active_color if self.isChecked() else self._bg_color
        radius = self.height() / 2
        painter.setBrush(QColor(color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)

    def hitButton(self, pos):
        return self.contentsRect().contains(pos)

    def mousePressEvent(self, event):
        self._auto_click = True
        self._press_global = event.globalPosition()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_global is not None and event.globalPosition() != self._press_global:
            self._auto_click = False
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Only handle simple clicks here; drags are handled by the thumb and
        # will trigger `toggled` which kicks off animation.
        if self._auto_click:
            self._auto_click = False
            self.setChecked(not self.isChecked())  # triggers start_animation
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        # Keep geometry coherent if you ever allow resizing
        thumb_margin = 3
        thumb_d = self.height() - 2 * thumb_margin
        left_x = thumb_margin
        right_x = self.width() - thumb_margin - thumb_d
        self._thumb.setFixedSize(thumb_d, thumb_d)
        self._thumb.move(right_x if self.isChecked() else left_x, thumb_margin)
        self._thumb.move_range = (left_x, right_x)
        super().resizeEvent(event)
