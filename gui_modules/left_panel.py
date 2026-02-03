# gui/modules/left_panel.py
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

# --- Cuando implementes el reproductor, descomentá esto ---
from gui_modules.video_frame import VideoFrame

# Nota: Los botones viven dentro de este panel (no son módulos separados),
# así que te dejo el bloque completo comentado para que lo actives cuando quieras:
#
from PySide6.QtWidgets import QPushButton, QWidget as QW, QVBoxLayout as QVL, QFileDialog
from PySide6.QtCore import Qt, Signal


class LeftPanel(QW):
    
    # Señal que se emite cuando se presiona el botón "Procesar video"
    processRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Estilo base del panel ---
        self.setStyleSheet("""
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
        self.setGraphicsEffect(shadow)

        # --- Layout del panel ---
        layout = QVL(self)
        layout.setContentsMargins(18, 18, 18, 18)

         # --- creo el main container ---
        main_container = QW()
        main_layout = QVL(main_container)
        main_layout.setSpacing(14)
        

        # ====== A) Reproductor / zona de video ======
        self.video_frame = VideoFrame()
        
        video_container = QW()
        video_v = QVL(video_container)
        video_v.setContentsMargins(20,20,20,20)
        
        video_v.addWidget(self.video_frame)
        
        main_layout.addWidget(video_container)

        # ====== B) Botones centrales grandes ======
        container = QW()
        v = QVL(container)
        v.setContentsMargins(0, 14, 0, 14)
        v.setSpacing(14)
        
        self.btn_load = self.create_button(text='Cargar video')
        self.btn_process = self.create_button(text='Procesar video')
        
        v.addWidget(self.btn_load, alignment=Qt.AlignHCenter)
        v.addWidget(self.btn_process, alignment=Qt.AlignHCenter)
        main_layout.addWidget(container)
        
        
         # --- agrego todo al layout ---
        layout.addWidget(main_container)
        
        
        # --- Conexión ---
        self.btn_process.clicked.connect(self.processRequested.emit)
        self.btn_load.clicked.connect(self.open_video)
        

        # (Opcional) Placeholder visible mientras todo está comentado:
        # placeholder = QLabel("LeftPanel listo.\nDescomentá VideoFrame y los botones cuando quieras.")
        # placeholder.setStyleSheet("color: #374151;")
        # placeholder.setAlignment(Qt.AlignCenter)
        # layout.addWidget(placeholder)

        # layout.addStretch()  # si querés empujar el contenido hacia arriba


    def create_button(self, text):
        btn = QPushButton(text)
        btn.setFixedWidth(220)
        btn.setFixedHeight(60)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-size: 20px;
                font-family: Intel;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1E4FD7;
            }
            QPushButton:pressed {
                background-color: #173FAF;
            }
        """)
        return btn
    
    
    def open_video(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Videos (*.mp4 *.avi *.mov *.mkv *.webm)")
        file_path, _ = file_dialog.getOpenFileName(self, "Seleccionar video", "", "Videos (*.mp4 *.avi *.mov *.mkv *.webm)")

        if file_path:
            try:
                # Guardás el path para reproducirlo o procesarlo
                print(f"Video seleccionado: {file_path}")
                self.video_frame.load_video(file_path)
            except Exception as e:
                print(f"Error al cargar el video: {e}")
