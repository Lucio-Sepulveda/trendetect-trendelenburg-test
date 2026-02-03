from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QFrame, QVBoxLayout
from PySide6.QtCore import Qt
import pandas as pd

class InfoPanel(QWidget):
    def __init__(self, summary_df, parent=None):
        super().__init__(parent)
        self.summary_df = summary_df
        self.init_ui()

    def init_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)
        x = 0
        y = 0

        for _, row in self.summary_df.iterrows():
            metric = row['Métrica']
            value = row['Valor']
            moment = row['Momento']

            # Crear bloque visual
            block = QFrame()
            block.setFrameShape(QFrame.StyledPanel)
            block.setStyleSheet("""
                QFrame {
                    background-color: #E5E7EB;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)

            block_layout = QVBoxLayout(block)
            block_layout.setSpacing(4)

            # Etiquetas
            metric_label = QLabel(f"<b>{metric}</b>")
            metric_label.setAlignment(Qt.AlignLeft)
            metric_label.setFont("Intel")
            metric_label.setStyleSheet("font-size: 25px; color: #374151;")

            value_str = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
            unit = "°" if "Ángulo" in metric else "seg" if metric == "Duración" else ""
            value_label = QLabel(f"{value_str} {unit}")
            value_label.setAlignment(Qt.AlignLeft)
            value_label.setFont("Intel")
            value_label.setStyleSheet("font-size: 20px; color: #6B7280;")

            block_layout.addWidget(metric_label)
            block_layout.addWidget(value_label)

            if not pd.isna(moment):
                moment_str = f"{moment:.2f}" if isinstance(moment, (int, float)) else str(moment)
                moment_label = QLabel(f"Momento: {moment_str} seg")
                moment_label.setAlignment(Qt.AlignLeft)
                block_layout.addWidget(moment_label)
                moment_label.setFont("Intel")
                moment_label.setStyleSheet("font-size: 20px; color: #6B7280;")
            
            main_layout.addWidget(block, x, y)
            y += 1
            if y >= 2:  # 2 bloques por fila
                y = 0
                x += 1