import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QProgressBar, QListWidget, 
    QListWidgetItem, QLabel, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QUrl
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QLinearGradient, QDesktopServices, QIcon
from scraper import ImageScraper
import os

class ExtractionWorker(QThread):
    progress_updated = pyqtSignal(int, int)
    extraction_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.downloader = ImageScraper()
    
    def run(self):
        try:
            images_data = self.downloader.extract_images_from_url(self.url)
            
            if not images_data or 'images' not in images_data or not images_data['images']:
                self.error_occurred.emit("No images found on this website")
                return
            
            def progress_callback(completed, total):
                self.progress_updated.emit(completed, total)
            
            result = self.downloader.download_images(images_data['images'], progress_callback)
            self.extraction_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class FloatingButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedHeight(45)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def enterEvent(self, event):
        self.animate_float(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animate_float(False)
        super().leaveEvent(event)
        
    def animate_float(self, floating):
        if floating:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2A2A2A, stop:1 #1A1A1A);
                    border: 2px solid #A020F0;
                    border-radius: 8px;
                    color: white;
                    font-size: 13pt;
                    font-family: 'Segoe UI';
                    font-weight: 600;
                    padding: 12px 24px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1A1A1A, stop:1 #000000);
                    border: 2px solid #8B00FF;
                    border-radius: 8px;
                    color: white;
                    font-size: 12pt;
                    font-family: 'Segoe UI';
                    font-weight: 600;
                    padding: 10px 20px;
                }
            """)

class GlowingLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.6);
                border: 2px solid #333333;
                border-radius: 8px;
                color: white;
                font-size: 13pt;
                font-family: 'Segoe UI';
                padding: 12px 16px;
                selection-background-color: #8B00FF;
            }
            QLineEdit:focus {
                border: 2px solid #8B00FF;
                background-color: rgba(0, 0, 0, 0.8);
            }
            QLineEdit:hover {
                border: 2px solid #555555;
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)

class CopyButton(QPushButton):
    def __init__(self, text="Copy"):
        super().__init__(text)
        self.setFixedSize(80, 35)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A1A, stop:1 #000000);
                border: 1px solid #8B00FF;
                border-radius: 6px;
                color: white;
                font-size: 10pt;
                font-family: 'Segoe UI';
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A2A2A, stop:1 #1A1A1A);
                border: 1px solid #A020F0;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CyberMyLife - Extract media")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        icon_path = os.path.join(os.getcwd(), "src", "icon", "favicon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        self.create_header(main_layout)
        self.create_input_section(main_layout)
        self.create_progress_section(main_layout)
        self.create_results_section(main_layout)
        self.create_buttons_section(main_layout)
        
        self.apply_dark_theme()
    
    def create_header(self, parent_layout):
        header_frame = QWidget()
        header_frame.setMinimumHeight(110)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        title = QLabel("CyberMyLife")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #8B00FF;
                font-size: 28pt;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
        """)
        
        subtitle = QLabel("Image scraper made with care, updates coming soon")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 12pt;
                font-family: 'Segoe UI';
                margin-top: 5px;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        parent_layout.addWidget(header_frame)
    
    def create_input_section(self, parent_layout):
        input_frame = QWidget()
        input_frame.setFixedHeight(60)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(15)
        
        self.url_input = GlowingLineEdit("Enter website URL to extract images")
        self.url_input.returnPressed.connect(self.start_extraction)
        
        self.extract_button = FloatingButton("Extract Images")
        self.extract_button.clicked.connect(self.start_extraction)
        
        input_layout.addWidget(self.url_input, 3)
        input_layout.addWidget(self.extract_button, 1)
        
        parent_layout.addWidget(input_frame)
    
    def create_progress_section(self, parent_layout):
        self.progress_frame = QWidget()
        self.progress_frame.setVisible(False)
        self.progress_frame.setFixedHeight(50)
        progress_layout = QVBoxLayout(self.progress_frame)
        
        self.progress_label = QLabel("Extracting images...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #8B00FF;
                font-size: 12pt;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 10px;
                text-align: center;
                background-color: #000000;
                color: white;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B00FF, stop:1 #A020F0);
                border-radius: 8px;
            }
        """)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(self.progress_frame)
    
    def create_results_section(self, parent_layout):
        results_frame = QWidget()
        results_layout = QVBoxLayout(results_frame)
        
        results_title = QLabel("Results")
        results_title.setStyleSheet("""
            QLabel {
                color: #8B00FF;
                font-size: 16pt;
                font-family: 'Segoe UI';
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(120)
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 0.6);
                border: 2px solid #333333;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI';
                font-size: 11pt;
                padding: 10px;
                selection-background-color: #8B00FF;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid rgba(51, 51, 51, 0.3);
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: rgba(139, 0, 255, 0.3);
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(139, 0, 255, 0.1);
            }
        """)
        
        results_layout.addWidget(results_title)
        results_layout.addWidget(self.results_list)
        
        parent_layout.addWidget(results_frame)
    
    def create_buttons_section(self, parent_layout):
        buttons_frame = QWidget()
        buttons_frame.setFixedHeight(80)
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.donate_button = FloatingButton("Donate")
        self.donate_button.clicked.connect(self.open_donate_page)
        
        self.contact_button = FloatingButton("Contact")
        self.contact_button.clicked.connect(self.open_contact_page)
        
        buttons_layout.addWidget(self.donate_button)
        buttons_layout.addWidget(self.contact_button)
        
        parent_layout.addWidget(buttons_frame)
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:1 #0A0A0A);
                color: white;
            }
            QWidget {
                background-color: transparent;
                color: white;
                font-family: 'Segoe UI';
            }
        """)
    
    def start_extraction(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.extract_button.setEnabled(False)
        self.extract_button.setText("Extracting...")
        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_list.clear()
        
        self.worker = ExtractionWorker(url)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.extraction_complete.connect(self.extraction_complete)
        self.worker.error_occurred.connect(self.extraction_error)
        self.worker.start()
    
    def update_progress(self, completed, total):
        progress = int((completed / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Downloading images... {completed}/{total}")
    
    def extraction_complete(self, result):
        self.progress_frame.setVisible(False)
        self.extract_button.setEnabled(True)
        self.extract_button.setText("Extract Images")
        
        folder_path = result['folder_path']
        successful = result['successful_downloads']
        failed = result['failed_downloads']
        
        self.results_list.addItem("Extraction completed successfully!")
        self.results_list.addItem(f"Saved to: {folder_path}")
        self.results_list.addItem(f"Downloaded: {len(successful)} images")
        
        if failed:
            self.results_list.addItem(f"Failed: {len(failed)} images")
        
        for img in successful[:8]:
            size_mb = img['size'] / (1024 * 1024)
            self.results_list.addItem(f"{img['filename']} ({size_mb:.2f} MB)")
        
        if len(successful) > 8:
            self.results_list.addItem(f"... and {len(successful) - 8} more images")
    
    def extraction_error(self, error_message):
        self.progress_frame.setVisible(False)
        self.extract_button.setEnabled(True)
        self.extract_button.setText("Extract Images")
        
        QMessageBox.critical(self, "Extraction Failed", f"Failed to extract images:\n\n{error_message}")
    
    def open_donate_page(self):
        donate_path = os.path.join(os.getcwd(), "src", "donate.html")
        donate_url = QUrl.fromLocalFile(donate_path)
        QDesktopServices.openUrl(donate_url)
    
    def open_contact_page(self):
        contact_path = os.path.join(os.getcwd(), "src", "contact.html")
        contact_url = QUrl.fromLocalFile(contact_path)
        QDesktopServices.openUrl(contact_url)