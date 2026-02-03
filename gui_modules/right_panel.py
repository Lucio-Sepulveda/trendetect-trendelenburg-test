from PySide6.QtWidgets import QWidget as QW, QVBoxLayout as QVL, QProgressBar, QLabel
from PySide6.QtCore import Qt

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from matplotlib.backends.backend_qtagg import FigureCanvas
from typing import List

from gui_modules.info_panel import InfoPanel



class MplCanvas(FigureCanvas):

    def __init__(self, fig, parent=None, width=5, height=4, dpi=100):
        fig.set_size_inches(width, height)
        fig.dpi = dpi
        super().__init__(fig)


class RightPanel(QW):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Estilo base del panel ---
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        # --- Layout del panel ---
        layout = QVL(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        
        
        # ====== A) Barra de progreso ======
        self.progress_container = self.create_progress_bar()
        layout.addWidget(self.progress_container, alignment=Qt.AlignmentFlag.AlignTop)
        
        # ====== B) Contenedor de informacion ======
        self.info_container = QW()
        self.layout_info = QVL(self.info_container)
        self.layout_info.setContentsMargins(18,18,18,18)
        self.layout_info.setSpacing(0)
        
        self.info_container.setStyleSheet("""
            QWidget {
                background-color: #F9FAFB;
                border-radius: 12px;
                border: 2px solid #E5E7EB;
                /* La fuente global la define MainWindow (Intel) */
            }
        """)
        
        layout.addWidget(self.info_container,stretch=1)
        self.info_panel = None
        self.chart_canvas = None
    
    
    def create_progress_bar(self):
        label = QLabel("Procesando...")
        label.setFont("Intel")
        label.setStyleSheet("font-size: 20px; color: #374151;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(7)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
            border-radius: 2px;
            background-color: #D1D5DB;
                }
            QProgressBar::chunk {
            border-radius: 2px;
            background-color: #3B82F6;
            }
        """)
        
        container = QW()
        v = QVL(container)
        
        container.setFixedHeight(80)
        v.setContentsMargins(20,10,20,10)
        
        container.setStyleSheet("""
            QWidget {
                background-color: #E5E7EB;
                border-radius: 12px;
                /* La fuente global la define MainWindow (Intel) */
            }
        """)
        
        # --- Sombra difuminada hacia abajo ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)       # qué tan difusa es la sombra
        shadow.setOffset(0, 6)         # desplazamiento hacia abajo
        shadow.setColor(QColor(0, 0, 0, 90))  # negro semitransparente
        container.setGraphicsEffect(shadow)
        
        v.addWidget(label,stretch=2,alignment=Qt.AlignmentFlag.AlignLeft)
        v.addWidget(self.progress_bar,stretch=1)
        container.hide()
        
        return container
    
    
    def update_progress_bar(self,percent):
        if self.progress_container.isHidden : self.progress_container.show()
        
        self.progress_bar.setValue(percent)
    
    
    def hidden_progress_bar(self):
        self.progress_container.hide()
    
    
    def show_results(self, results:List[object]):
        self.show_info_results(info_df=results[0])
        self.show_chart(fig=results[1])
    
    
    def show_info_results(self, info_df):
        if self.info_panel:
            self.layout_info.removeWidget(self.info_panel)
            self.info_panel.deleteLater()
            self.info_panel = None
        
        self.info_panel = InfoPanel(info_df)
        self.layout_info.addWidget(self.info_panel)
    
    
    def show_chart(self, fig):
        if self.chart_canvas:
            self.layout_info.removeWidget(self.chart_canvas)
            self.chart_canvas.deleteLater()
            self.chart_canvas = None
        
        self.chart_canvas = MplCanvas(fig)
        self.layout_info.addWidget(self.chart_canvas)
        
