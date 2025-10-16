import resources_rc

styles = """
    
 QWidget {
    background-color: #1e1e1e;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #f0f0f0;
}

QPushButton {
    padding: 6px 14px;
    font-size: 13px;
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 8px;
    color: white;
    transition: all 0.3s ease;
}

QPushButton:hover {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    box-shadow: 0 0 4px 1px rgba(0, 120, 215, 0.5);
}

QPushButton:pressed {
    background-color: #0078d7;
    border: 1px solid #005a9e;
}

QListWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: Consolas, monospace;
    font-size: 13px;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 6px;
}

QListWidget::item:selected {
    background-color: #3a75c4;
    color: white;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #333;
    border-radius: 4px;
}

QGroupBox {
    border: 1px solid #444;
    border-radius: 10px;
    margin-top: 10px;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    font-weight: bold;
    color: #dddddd;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #888;
    background-color: #48574e;
}

QCheckBox::indicator:checked {
    background-color: #383837;
    border: 1px solid #789483;
    image: url(:/assets/icons-check.png);
}

QCheckBox:disabled {
    color: #777777;
}

QCheckBox::indicator:disabled {
    image: url(:/assets/check-disabled.png);
    width: 15px;
    height: 15px;
    border: 1px solid #555555;
    background-color: #2a2a2a;
    border-radius: 3px;
}

QCheckBox::indicator:checked:disabled {

    background-color: #444444;
    border: 1px solid #666666;
}

QCheckBox::indicator:disabled:hover,
QCheckBox::indicator:disabled:pressed {
    background-color: #2a2a2a;
    border: 1px solid #555555;
}

QToolTip {

    background-color: #2b2b2b;
    border: 2px solid #c8c8c8;
    border-radius: 8px;
    padding: 4px;
    font-size: 12px;
    font-family: "Segoe UI", sans-serif, white;
    color: white;
    margin: -1px;
}

QLineEdit {
    background: #2b2b2b;
    border: none;
    border-radius: 8px;
    border-bottom: 1px solid #444;
    padding: 3px;
    color: #f0f0f0;
    min-height: 22px;
    max-height: 22px;
    selection-background-color: #0078d7;
    selection-color: white;     
}

QLineEdit:disabled {
    border-bottom: 2px solid #b05a6c; 
    
}


QLineEdit:focus {
    border-bottom: 1.5px solid #dbc98c;
}


QLineEdit:hover {
    border-bottom: 1.5px solid #5a5a5a;
}

QLineEdit:focus:hover {
    border-bottom: 2px solid #cfc186;
    background: #32353b;
}

QScrollArea {
    border: none;
    background: #2b2b2b;
}





"""