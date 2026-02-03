# gui/modules/video_frame.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent


# --- Para el player cuando quieras usarlo ---
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.video_path = None

        # --- Estado inicial: aceptar drag & drop ---
        self.setAcceptDrops(True)

        # --- Estilo inicial (placeholder) ---
        self.setStyleSheet("""
            QWidget {
                border: 5px dashed #D1D5DB;
                border-radius: 12px;
                background-color: #E5E7EB;
            }
        """)

        self.setMinimumWidth(150)
        self.setMinimumHeight(270)  # algo más razonable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Placeholder inicial ---
        self.placeholder = QLabel("Arrastrá tu video aquí")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 20px;
                font-family: Intel;
            }
        """)
        layout.addWidget(self.placeholder)

        # --- Reproductor (cuando lo actives) ---
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        self.video_widget.hide()

    # ==========================
    # Drag & Drop
    # ==========================
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            self.video_path = urls[0].toLocalFile()
            print(f"Video cargado: {self.video_path}")
            self.load_video(self.video_path)

    # ==========================
    # Lógica de carga de video
    # ==========================
    def load_video(self, path: str):
        """Guarda path y cambia placeholder por el player"""
        self.video_path = path

        # --- Reemplazar placeholder ---
        if self.placeholder:
            self.placeholder.hide()

        # --- Mostrar video ---
        self.video_widget.show()
        self.media_player.setSource(path)
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.media_player.play()
        self.media_player

        # Por ahora solo feedback:
        # self.placeholder.setText(f"Video listo:\n{path.split('/')[-1]}")
        # self.placeholder.show()
