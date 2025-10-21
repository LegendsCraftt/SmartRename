from PyQt6.QtWidgets import QWidget, QSizePolicy, QFrame

from PyQt6.QtWidgets import QFrame


def h_separator(parent=None, thickness=1):
    w = QWidget(parent)
    w.setObjectName("menuSeparator")
    w.setFixedHeight(thickness)
    w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return w

def v_separator(parent=None, thickness=1):
    w = QWidget(parent)
    w.setObjectName("menuVSeparator")
    w.setFixedWidth(thickness)
    w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    return w



def h_line(line_width=1, parent=None):
    line = QFrame(parent)
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)  # or Plain
    line.setLineWidth(line_width)
    return line
