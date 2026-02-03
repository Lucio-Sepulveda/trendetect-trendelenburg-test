# gui/modules/up_bar.py
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QFrame, QVBoxLayout
from PySide6.QtCore import Signal, Qt


class UpBar(QWidget):
    # Señal que se emite cuando se presiona el botón "Guardar"
    saveRequested = Signal()
    loadRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Widgets ---
        self.title_label = QLabel("KinotraK - TrendetecT")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet("""
            color: #374151;
            font-size: 35px;
            font-family: Intel;
            font-weight: bold;
        """)

        self.save_button = QPushButton("Guardar datos")
        self.save_button.setFixedWidth(150)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB;
                color: #000000;
                font-size: 20px;
                font-family: Intel;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
            QPushButton:pressed {
                background-color: #9ca3af;
            }
        """)
        
        self.load_button = QPushButton("Cargar datos")
        self.load_button.setFixedWidth(150)
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB;
                color: #000000;
                font-size: 20px;
                font-family: Intel;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
            QPushButton:pressed {
                background-color: #9ca3af;
            }
        """)

        # Línea divisoria inferior
        self.bottom_line = QFrame()
        self.bottom_line.setFrameShape(QFrame.HLine)
        self.bottom_line.setFrameShadow(QFrame.Sunken)
        self.bottom_line.setStyleSheet("color: #E5E7EB;")

        # --- Layout superior (título + botón) ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.save_button)
        top_layout.addWidget(self.load_button)

        # --- Layout principal (barra + línea inferior) ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 0)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.bottom_line)

        # --- Conexión ---
        self.save_button.clicked.connect(self.saveRequested.emit)
        self.load_button.clicked.connect(self.loadRequested.emit)
