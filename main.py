import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QFileDialog, QGraphicsView, 
                               QGraphicsScene, QMessageBox, QGraphicsItem, QGraphicsRectItem)
from PySide6.QtGui import QPixmap, QPen, QColor, QShortcut, QKeySequence, QPainter, QIcon
from PySide6.QtCore import Qt, QRectF, QPointF, QUrl, QByteArray, QBuffer, QIODevice

# --- Resource Helper for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- The Coffee Theme Style Sheet ---
COFFEE_THEME = """
QWidget {
    background-color: #2b1f1a; /* Dark Espresso */
    color: #ebd9c8; /* Cream/Latte text */
    font-family: "Segoe UI", sans-serif;
}
QPushButton {
    background-color: #7b3e2b; /* Warm reddish-brown */
    border: 2px solid #52261a;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #9c4c34; /* Lighter reddish-brown on hover */
}
QPushButton:pressed {
    background-color: #52261a;
}
QPushButton:disabled {
    background-color: #3d2b24;
    color: #75655d;
    border: 2px solid #2b1f1a;
}
/* Style specifically for the Mode Toggle button to make it stand out */
QPushButton#ModeToggle {
    background-color: #3d2b24;
    border: 2px solid #d45d3c;
    color: #d45d3c;
}
QPushButton#ModeToggle:hover {
    background-color: #52261a;
}
QGraphicsView {
    background-color: #1c130f; /* Very dark background for the canvas */
    border: 2px solid #52261a;
    border-radius: 6px;
}
"""

class CropBox(QGraphicsRectItem):
    """The interactive 16:9 bounding box."""
    def __init__(self, image_rect):
        super().__init__()
        self.image_rect = image_rect
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        pen = QPen(QColor("#d45d3c"), 3, Qt.PenStyle.DashLine)
        self.setPen(pen)
        
    def wheelEvent(self, event):
        zoom_factor = 1.05 if event.delta() > 0 else 0.95
        
        current_rect = self.rect()
        new_width = current_rect.width() * zoom_factor
        new_height = current_rect.height() * zoom_factor
        
        if new_width > self.image_rect.width() or new_height > self.image_rect.height():
            return
        if new_width < 160 or new_height < 90:
            return
            
        center = current_rect.center()
        new_rect = QRectF(center.x() - new_width / 2, 
                          center.y() - new_height / 2, 
                          new_width, new_height)
                          
        scene_bounds = QRectF(self.pos().x() + new_rect.left(),
                              self.pos().y() + new_rect.top(),
                              new_rect.width(), new_rect.height())
        
        if not self.image_rect.contains(scene_bounds):
            return
            
        self.setRect(new_rect)
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos = value
            rect = self.rect()
            
            min_x = self.image_rect.left() - rect.left()
            max_x = self.image_rect.right() - rect.right()
            min_y = self.image_rect.top() - rect.top()
            max_y = self.image_rect.bottom() - rect.bottom()
            
            clamped_x = min(max(new_pos.x(), min_x), max_x)
            clamped_y = min(max(new_pos.y(), min_y), max_y)
            
            return QPointF(clamped_x, clamped_y)
            
        return super().itemChange(change, value)

# --- Custom Canvas for Drag & Drop ---
class CanvasView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile()
            if url.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.main_window.load_image_from_path(file_path)


class ThumbnailApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thumbnail Resizer")
        self.setMinimumSize(800, 550)
        self.setStyleSheet(COFFEE_THEME)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        
        self.current_image_path = None
        self.original_pixmap = None
        self.crop_box = None
        
        # --- State Tracking for Modes ---
        self.is_crop_mode = True 
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        toolbar_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load Image")
        self.btn_load.clicked.connect(self.open_file_dialog)
        
        # --- The New Toggle Button ---
        self.btn_toggle_mode = QPushButton("Mode: CROP")
        self.btn_toggle_mode.setObjectName("ModeToggle")
        self.btn_toggle_mode.clicked.connect(self.toggle_mode)
        
        self.btn_crop = QPushButton("Crop & Save Thumbnail (Enter)")
        self.btn_crop.clicked.connect(self.process_and_save)
        self.btn_crop.setEnabled(False) 
        
        toolbar_layout.addWidget(self.btn_load)
        toolbar_layout.addWidget(self.btn_toggle_mode)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_crop)
        main_layout.addLayout(toolbar_layout)

        self.scene = QGraphicsScene()
        self.view = CanvasView(self.scene, self)
        main_layout.addWidget(self.view)
        
        self.shortcut_enter = QShortcut(QKeySequence("Return"), self)
        self.shortcut_enter.activated.connect(self.btn_crop.click)
        
        self.shortcut_numpad_enter = QShortcut(QKeySequence("Enter"), self)
        self.shortcut_numpad_enter.activated.connect(self.btn_crop.click)

    # --- Mode Toggle Logic ---
    def toggle_mode(self):
        self.is_crop_mode = not self.is_crop_mode
        
        if self.is_crop_mode:
            self.btn_toggle_mode.setText("Mode: CROP")
            self.btn_crop.setText("Crop & Save Thumbnail (Enter)")
            if self.crop_box:
                self.crop_box.setVisible(True)
        else:
            self.btn_toggle_mode.setText("Mode: STRETCH")
            self.btn_crop.setText("Stretch & Save Thumbnail (Enter)")
            if self.crop_box:
                self.crop_box.setVisible(False)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path):
        self.current_image_path = file_path
        self.original_pixmap = QPixmap(file_path)
        
        self.scene.clear()
        
        self.scene.addPixmap(self.original_pixmap)
        image_rect = QRectF(self.original_pixmap.rect())
        self.scene.setSceneRect(image_rect)
        
        img_w = image_rect.width()
        img_h = image_rect.height()
        
        if img_w / img_h > 16 / 9:
            box_h = img_h
            box_w = box_h * (16 / 9)
        else:
            box_w = img_w
            box_h = box_w * (9 / 16)
            
        box_rect = QRectF(0, 0, box_w, box_h)
        self.crop_box = CropBox(image_rect)
        self.crop_box.setRect(box_rect)
        
        center_x = (img_w - box_w) / 2
        center_y = (img_h - box_h) / 2
        self.crop_box.setPos(center_x, center_y)
        
        self.scene.addItem(self.crop_box)
        
        # Respect the current mode visibility when loading a new image
        self.crop_box.setVisible(self.is_crop_mode)
        
        self.btn_crop.setEnabled(True)
        self.view.fitInView(image_rect, Qt.AspectRatioMode.KeepAspectRatio)

    # --- Renamed to reflect both Crop and Stretch ---
    def process_and_save(self):
        if not self.original_pixmap:
            return
            
        if self.is_crop_mode:
            # Mode 1: Crop
            if not self.crop_box: return
            crop_rect_scene = self.crop_box.mapToScene(self.crop_box.rect()).boundingRect()
            crop_rect_int = crop_rect_scene.toRect()
            processed_pixmap = self.original_pixmap.copy(crop_rect_int)
        else:
            # Mode 2: Stretch (Take the whole image)
            processed_pixmap = self.original_pixmap
        
        # Both modes scale exactly to 1280x720 ignoring aspect ratio
        final_thumbnail = processed_pixmap.scaled(
            1280, 720, 
            Qt.AspectRatioMode.IgnoreAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # --- 2MB File Size Check & Auto-Compress Logic ---
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        
        # Try pure PNG first
        final_thumbnail.save(buffer, "PNG")
        
        MAX_BYTES = 2 * 1024 * 1024 # 2MB limit
        directory = os.path.dirname(self.current_image_path)
        base_name = "RESIZED"
        used_compression = False
        
        if byte_array.size() <= MAX_BYTES:
            ext = ".png"
            img_format = "PNG"
            quality = -1 # default PNG quality
        else:
            used_compression = True
            ext = ".jpg"
            img_format = "JPG"
            quality = 95 # Start with high quality JPG
            
            # Loop and reduce quality until it fits under 2MB
            while quality > 10:
                byte_array.clear()
                buffer.seek(0)
                final_thumbnail.save(buffer, img_format, quality)
                if byte_array.size() <= MAX_BYTES:
                    break
                quality -= 5 
                
        buffer.close()

        # --- Resolve Naming ---
        save_path = os.path.join(directory, f"{base_name}{ext}")
        counter = 1
        while os.path.exists(save_path):
            save_path = os.path.join(directory, f"{base_name} ({counter}){ext}")
            counter += 1
        
        # --- Final Save ---
        success = final_thumbnail.save(save_path, img_format, quality)
        
        if success:
            action_text = "cropped" if self.is_crop_mode else "stretched"
            msg = f"Thumbnail perfectly {action_text}, resized, and saved to:\n{save_path}"
            if used_compression:
                msg += f"\n\n(Auto-compressed to JPG at {quality}% quality to stay under YouTube's 2MB limit!)"
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", "Something went wrong while saving the image.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThumbnailApp()
    window.show()
    sys.exit(app.exec())
