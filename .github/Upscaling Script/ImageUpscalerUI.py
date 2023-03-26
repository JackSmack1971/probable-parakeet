import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QFormLayout,
    QWidget,
    QProgressBar,
    QVBoxLayout,
    QMessageBox,
    QToolTip
)
from upscaling_script import upscale_images
class ImageUpscalerUI(QMainWindow):
    def __init__(self):
        super().__init__() 

        # Set window title
        self.setWindowTitle("Image Upscaler") 

        # Set window size
        self.setGeometry(200, 200, 500, 400) 

        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget) 

        # Create vertical layout for input fields
        input_layout = QVBoxLayout() 

        # Add input file selection button
        self.input_file_button = QPushButton("Select Input Files", self)
        self.input_file_button.setToolTip("Click to select input files")
        self.input_file_button.clicked.connect(self.select_input_files)
        input_layout.addWidget(self.input_file_button) 

        # Add output directory selection button
        self.output_dir_button = QPushButton("Select Output Directory", self)
        self.output_dir_button.setToolTip("Click to select output directory")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        input_layout.addWidget(self.output_dir_button) 

        # Add upscaling method selection combo box
        self.method_combo_box = QComboBox(self)
        self.method_combo_box.setToolTip("Select the upscaling method")
        self.method_combo_box.addItems(["nearest", "bilinear", "bicubic", "lanczos", "edsr"])
        input_layout.addWidget(QLabel("Upscaling Method:"))
        input_layout.addWidget(self.method_combo_box) 

        # Add scale factor selection spin box
        self.scale_factor_spinbox = QSpinBox(self)
        self.scale_factor_spinbox.setToolTip("Select the scale factor")
        self.scale_factor_spinbox.setMinimum(1)
        self.scale_factor_spinbox.setMaximum(10)
        self.scale_factor_spinbox.setValue(4)
        input_layout.addWidget(QLabel("Scale Factor:"))
        input_layout.addWidget(self.scale_factor_spinbox) 

        # Add output format selection combo box
        self.output_format_combo_box = QComboBox(self)
        self.output_format_combo_box.setToolTip("Select the output image format")
        self.output_format_combo_box.addItems(["jpg", "png", "bmp"])
        input_layout.addWidget(QLabel("Output Format:"))
        input_layout.addWidget(self.output_format_combo_box) 

        # Add compression level selection spin box
        self.compression_spinbox = QSpinBox(self)
        self.compression_spinbox.setToolTip("Select the output image compression level")
        self.compression_spinbox.setMinimum(0)
        self.compression_spinbox.setMaximum(100)
        self.compression_spinbox.setValue(80)
        input_layout.addWidget(QLabel("Compression Level:"))
        input_layout.addWidget(self.compression_spinbox) 

        # Add progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        input_layout.addWidget(self.progress_bar) 

        # Add upscale button
        upscale_button = QPushButton("Start Upscaling", self)
        upscale_button.setToolTip("Click to start the upscaling process")
        upscale_button.clicked.connect(self.upscale_images)
        input_layout.addWidget(upscale_button) 

        # Set layout for central widget
        central_widget.setLayout(input_layout) 

        # Initialize input and output paths to None
        self.input_paths = []
        self.output_dir = None
    def select_input_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Select Input Files", "", "Image Files (*.jpg *.jpeg *.png *.bmp)", options=options
        )
        if file_names:
            self.input_paths = file_names
            self.input_file_button.setText(f"Selected {len(file_names)} Files") 

    def select_output_dir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if output_dir:
            self.output_dir = output_dir
            self.output_dir_button.setText(f"Selected Output Directory: {output_dir}")
    def upscale_images(self):
        if self.input_paths and self.output_dir:
            # Call upscale_images function with selected parameters
            method = self.method_combo_box.currentText()
            scale_factor = self.scale_factor_spinbox.value()
            output_format = self.output_format_combo_box.currentText()
            compression = self.compression_spinbox.value()
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Upscaling images...") 

            try:
                upscale_images(self.input_paths, self.output_dir, method, scale_factor, output_format, compression, self.update_progress_bar)
                self.progress_bar.setFormat("Images upscaled!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e), QMessageBox.Ok)
                self.progress_bar.setFormat("Upscaling failed.") 

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
