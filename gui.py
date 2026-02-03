# gui/gui.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QFileDialog
)
from PySide6.QtCore import QThreadPool

from gui_modules.up_bar import UpBar
from gui_modules.left_panel import LeftPanel
from gui_modules.right_panel import RightPanel

from core.tools.qt_thread import Worker
import sys

from typing import List

from core.trendetect import TrendetecT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KinotraK - TrendetecT")
        
        # --- Background ---
        self.setStyleSheet("background-color: #F9FAFB; font-family: Intel;")
        self.setMinimumSize(900, 600)

        # --- Widget central ---
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central)

        # --- Arriba: barra superior ---
        self.up_bar = UpBar()
        self.setMenuWidget(self.up_bar)

        # --- Columna izquierda ---
        left_layout = QVBoxLayout()
        self.left_panel = LeftPanel()
        left_layout.addWidget(self.left_panel)
        
        self.left_panel.processRequested.connect(self.process_video)

        # --- Columna derecha ---
        right_layout = QVBoxLayout()
        self.right_panel = RightPanel()
        right_layout.addWidget(self.right_panel)

        # Agregar columnas al layout principal
        main_layout.addLayout(left_layout, 2)   # peso 2 para columna izquierda
        main_layout.addLayout(right_layout, 3)  # peso 3 para columna derecha
        
        # --- Lógica de procesamiento ---
        self.trendetect = TrendetecT()
        self.threadpool = QThreadPool()
        
        # --- Señales de guardado y carga de procesamientos ---
        self.up_bar.saveRequested.connect(self.save_results)
        self.up_bar.loadRequested.connect(self.load_results)
        


    def process_video(self):
        if not self.uploaded_video():
            return

        worker = Worker(self.trendetect.process_video, self.get_video_path())
        
        worker.signals.result.connect(self.on_finished)
        worker.signals.progress.connect(self.right_panel.update_progress_bar)
        worker.signals.error.connect(self.on_error)
        worker.signals.result.connect(self.right_panel.show_results)
        
        self.threadpool.start(worker)
    

    def on_finished(self):
        self.right_panel.hidden_progress_bar()
    

    def on_error(self, error_msg):
        print(f"Error: {error_msg}")
        # Muestra el error en la GUI

    
    def uploaded_video(self):
        return self.left_panel.video_frame.video_path is not None
    
    
    def get_video_path(self):
        return self.left_panel.video_frame.video_path
    
    
    def save_results(self):
        if self.trendetect is None:
            return
        
        if self.trendetect.angle_series.empty:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar resultados", 
            "",     # Initial directory (empty string means current working directory)
            "Archivos CSV (*.csv);;Todos los archivos (*)"
            )
        
        if file_path:
            self.trendetect.save_results(file_path)
         
    
    
    def load_results(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Cargar resultados", 
            "",     # Initial directory (empty string means current working directory)
            "Archivos CSV (*.csv);;Todos los archivos (*)"
            )
        
        if file_path:
            results = self.trendetect.load_results(file_path)
            
            if results is not None:
                self.right_panel.show_results(results)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
