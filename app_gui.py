import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
                            QRadioButton, QButtonGroup, QFileDialog, QCheckBox,
                            QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import file_to_json
import url_to_json

class ContentWorker(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)  # New signal for detailed status updates

    def __init__(self, input_type, title, content, url, custom_thumbnail):
        super().__init__()
        self.input_type = input_type
        self.title = title
        self.content = content
        self.url = url
        self.custom_thumbnail = custom_thumbnail
        print(f"ContentWorker initialized with thumbnail: {custom_thumbnail}")  # Debug info

    def run(self):
        try:
            if self.input_type == "text":
                # Save content to temporary file
                temp_file = "input/input.txt"
                os.makedirs("input", exist_ok=True)
                
                self.status_update.emit("Creating input file...")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(self.content)
                
                self.progress.emit("Processing text input...")
                self.status_update.emit("Generating content from text...")
                output_folder = file_to_json.process_file(temp_file, self.title)
            else:
                self.progress.emit("Processing URL...")
                self.status_update.emit("Fetching content from URL...")
                output_folder = url_to_json.process_url(self.url, self.title)
            
            self.status_update.emit(f"✅ Content generated successfully!")
            self.status_update.emit(f"📁 Output folder: {output_folder}")
            
            # If images were found, show count
            image_folder = os.path.join(output_folder)
            if os.path.exists(image_folder):
                image_count = len([f for f in os.listdir(image_folder) 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                self.status_update.emit(f"🖼️ Images downloaded: {image_count}")

            self.finished.emit(output_folder)
        except Exception as e:
            error_msg = str(e)
            self.status_update.emit(f"❌ Error: {error_msg}")
            self.error.emit(error_msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Content Gatherer")
        self.setup_ui()
        
        # Add status text area
        self.status_area = QTextEdit()
        self.status_area.setReadOnly(True)
        self.status_area.setMinimumHeight(100)
        self.status_area.setPlaceholderText("Status updates will appear here...")

    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Input type selection
        input_type_layout = QHBoxLayout()
        self.text_radio = QRadioButton("Text Input")
        self.url_radio = QRadioButton("URL Input")
        self.text_radio.setChecked(True)
        input_type_layout.addWidget(self.text_radio)
        input_type_layout.addWidget(self.url_radio)
        layout.addLayout(input_type_layout)

        # Group radio buttons
        self.input_group = QButtonGroup()
        self.input_group.addButton(self.text_radio)
        self.input_group.addButton(self.url_radio)
        self.input_group.buttonClicked.connect(self.on_input_type_changed)

        # Title input (only for text mode)
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        self.title_container = QWidget()
        self.title_container.setLayout(title_layout)
        layout.addWidget(self.title_container)

        # Content input
        self.content_label = QLabel("Content:")
        layout.addWidget(self.content_label)
        self.content_input = QTextEdit()
        layout.addWidget(self.content_input)

        # URL input
        self.url_label = QLabel("URL:")
        layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        # Custom thumbnail checkbox and file selection
        thumbnail_layout = QHBoxLayout()
        self.thumbnail_check = QCheckBox("Use Custom Thumbnail")
        self.thumbnail_check.setChecked(False)  # Initialize as unchecked
        self.thumbnail_check.stateChanged.connect(self.on_thumbnail_checked)
        self.thumbnail_button = QPushButton("Select Thumbnail")
        self.thumbnail_button.clicked.connect(self.select_thumbnail)
        self.thumbnail_button.setEnabled(False)  # Initially disabled
        thumbnail_layout.addWidget(self.thumbnail_check)
        thumbnail_layout.addWidget(self.thumbnail_button)
        layout.addLayout(thumbnail_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Status area
        layout.addWidget(self.status_area)
        
        # Generate button
        self.generate_button = QPushButton("Generate Content")
        self.generate_button.clicked.connect(self.generate_content)
        layout.addWidget(self.generate_button)

        # Set initial state
        self.on_input_type_changed()
        self.thumbnail_path = None
        self.resize(600, 400)

    def on_input_type_changed(self):
        is_text = self.text_radio.isChecked()
        self.content_label.setVisible(is_text)
        self.content_input.setVisible(is_text)
        self.url_label.setVisible(not is_text)
        self.url_input.setVisible(not is_text)
        self.title_container.setVisible(is_text)  # Only show title input for text mode

    def on_thumbnail_checked(self, state):
        print(f"Checkbox state changed: {state}")  # Debug print
        self.thumbnail_button.setEnabled(bool(state))  # Convert state to boolean

    def select_thumbnail(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select Thumbnail Image",
                "",
                "Images (*.png *.jpg *.jpeg)"
            )
            if file_name:
                # Copy the image to the output directory
                output_dir = "input"  # Use same directory as your text input
                os.makedirs(output_dir, exist_ok=True)
                
                # Save the path for later use
                self.thumbnail_path = file_name
                
                # Update button text to show selected file
                short_name = os.path.basename(file_name)
                if len(short_name) > 20:
                    short_name = short_name[:17] + "..."
                self.thumbnail_button.setText(f"Selected: {short_name}")
                
                print(f"Selected thumbnail: {file_name}")  # Debug info
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error selecting thumbnail: {str(e)}")
            self.thumbnail_path = None

    def generate_content(self):
        input_type = "text" if self.text_radio.isChecked() else "url"
        
        if input_type == "text":
            title = self.title_input.text().strip()
            content = self.content_input.toPlainText().strip()
            if not title:
                QMessageBox.warning(self, "Error", "Please enter a title")
                return
            if not content:
                QMessageBox.warning(self, "Error", "Please enter content")
                return
        else:  # URL mode
            title = ""  # Will be extracted from the URL content
            content = ""
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "Error", "Please enter URL")
                return

        # Disable UI while processing
        self.generate_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setFormat("Processing...")
        self.progress_bar.setRange(0, 0)  # Indeterminate mode

        # Clear status area
        self.status_area.clear()
        self.add_status("Starting content generation...")

        # Start worker thread
        self.worker = ContentWorker(
            input_type=input_type,
            title=title,
            content=content,
            url=url,
            custom_thumbnail=self.thumbnail_path if self.thumbnail_check.isChecked() else None
        )
        self.worker.finished.connect(self.on_generation_complete)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.error.connect(self.on_error)
        self.worker.status_update.connect(self.add_status)
        self.worker.start()

    def on_generation_complete(self, output_folder):
        self.generate_button.setEnabled(True)
        self.progress_bar.hide()
        QMessageBox.information(self, "Success", f"Content generated successfully!\nOutput folder: {output_folder}")

    def on_progress_update(self, message):
        self.progress_bar.setFormat(message)

    def add_status(self, message):
        self.status_area.append(message)
        # Scroll to bottom
        scrollbar = self.status_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_error(self, error_message):
        self.generate_button.setEnabled(True)
        self.progress_bar.hide()
        self.add_status(f"❌ Error: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
