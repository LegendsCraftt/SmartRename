from pathlib import Path

from PyQt6.QtCore import QFile, QTextStream
from assets.resources import resources_rc



# -- When Compiling --

qss = QFile(":/assets/resources/style.qss")

if qss.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
    stream = QTextStream(qss)
    stream = stream.readAll()
else:
    print(f"Error opening {qss.fileName()}: {qss.errorString()}")


# -- While Dev --

# qss = Path(resources_rc.__file__).parent / "style.qss"
#
# with open(qss, "r", encoding="utf-8") as f:
#     stream = f.read()
