# from stitcher_sift import ImageStitcher
# from stitcher_superpoint import SuperPointStitcher
#
# import cv2
# import sys
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QFileDialog, QLabel, QComboBox,
#     QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QMessageBox, QTabWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QProgressBar
# )
# from PyQt5.QtGui import QIcon, QPixmap, QImage
# from PyQt5.QtCore import Qt
#
#
# class StitchingApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle("Video Stitching App")
#         self.setWindowIcon(QIcon("icon.png"))  # Додайте шлях до вашої іконки
#         self.resize(800, 600)
#
#         # Main layout
#         main_layout = QHBoxLayout()
#
#         # Left-side layout for controls
#         control_layout = QVBoxLayout()
#
#         # Dropdown to select method
#         self.method_label = QLabel("Метод зшивання:")
#         self.method_combo = QComboBox()
#         self.method_combo.addItems(["sift", "superpoint"])
#         self.method_combo.currentTextChanged.connect(self.update_parameters_visibility)
#
#         # Dropdown to select transformation type
#         self.transformation_label = QLabel("Тип трансформації:")
#         self.transformation_combo = QComboBox()
#         self.transformation_combo.addItems(["homography", "affine"])
#
#         # SIFT parameters
#         sift_layout = QFormLayout()
#         self.lowe_ratio_input = QDoubleSpinBox()
#         self.lowe_ratio_input.setRange(0.1, 1.0)
#         self.lowe_ratio_input.setSingleStep(0.1)
#         self.lowe_ratio_input.setValue(0.6)
#         sift_layout.addRow("Lowe Ratio:", self.lowe_ratio_input)
#
#         self.ransac_thresh_input = QDoubleSpinBox()
#         self.ransac_thresh_input.setRange(0.1, 10.0)
#         self.ransac_thresh_input.setSingleStep(0.5)
#         self.ransac_thresh_input.setValue(2.0)
#         sift_layout.addRow("RANSAC Threshold:", self.ransac_thresh_input)
#
#         # SuperPoint parameters
#         superpoint_layout = QFormLayout()
#         self.nms_radius_input = QSpinBox()
#         self.nms_radius_input.setRange(1, 20)
#         self.nms_radius_input.setValue(4)
#         superpoint_layout.addRow("NMS Radius:", self.nms_radius_input)
#
#         self.keypoint_threshold_input = QDoubleSpinBox()
#         self.keypoint_threshold_input.setRange(0.0001, 0.1)
#         self.keypoint_threshold_input.setSingleStep(0.001)
#         self.keypoint_threshold_input.setValue(0.001)
#         superpoint_layout.addRow("Keypoint Threshold:", self.keypoint_threshold_input)
#
#         self.max_keypoints_input = QSpinBox()
#         self.max_keypoints_input.setRange(100, 5000)
#         self.max_keypoints_input.setValue(1024)
#         superpoint_layout.addRow("Max Keypoints:", self.max_keypoints_input)
#
#         # Frame interval parameter
#         self.frame_interval_input = QSpinBox()
#         self.frame_interval_input.setRange(1, 100)
#         self.frame_interval_input.setValue(20)
#
#         # Tab widget for parameters
#         self.tab_widget = QTabWidget()
#         self.tab_sift = QWidget()
#         self.tab_superpoint = QWidget()
#         self.tab_sift.setLayout(sift_layout)
#         self.tab_superpoint.setLayout(superpoint_layout)
#
#         self.tab_widget.addTab(self.tab_sift, "SIFT Parameters")
#         self.tab_widget.addTab(self.tab_superpoint, "SuperPoint Parameters")
#
#         # Video file selection
#         self.video_path_label = QLabel("Файл відео:")
#         self.video_path_input = QLineEdit()
#         self.browse_button = QPushButton("Огляд")
#         self.browse_button.clicked.connect(self.browse_file)
#
#         # Output folder selection
#         self.output_folder_label = QLabel("Папка для збереження результату:")
#         self.output_folder_input = QLineEdit()
#         self.output_browse_button = QPushButton("Огляд")
#         self.output_browse_button.clicked.connect(self.browse_output_folder)
#
#         # Start stitching button
#         self.stitch_button = QPushButton("Запустити зшивання")
#         self.stitch_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
#         self.stitch_button.clicked.connect(self.start_stitching)
#
#         # Progress bar
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setValue(0)
#
#         # Add widgets to control layout
#         control_layout.addWidget(self.method_label)
#         control_layout.addWidget(self.method_combo)
#         control_layout.addWidget(self.transformation_label)
#         control_layout.addWidget(self.transformation_combo)
#         control_layout.addWidget(QLabel("Інтервал кадрів:"))
#         control_layout.addWidget(self.frame_interval_input)
#         control_layout.addWidget(self.tab_widget)
#         control_layout.addWidget(self.video_path_label)
#         control_layout.addWidget(self.video_path_input)
#         control_layout.addWidget(self.browse_button)
#         control_layout.addWidget(self.output_folder_label)
#         control_layout.addWidget(self.output_folder_input)
#         control_layout.addWidget(self.output_browse_button)
#         control_layout.addWidget(self.stitch_button)
#         control_layout.addWidget(self.progress_bar)
#
#         # Right-side layout for image display
#         image_layout = QVBoxLayout()
#         self.result_image_label = QLabel()
#         self.result_image_label.setAlignment(Qt.AlignCenter)
#         image_layout.addWidget(self.result_image_label)
#
#         # Add layouts to main layout
#         main_layout.addLayout(control_layout, 1)
#         main_layout.addLayout(image_layout, 2)
#
#         # Set central widget
#         container = QWidget()
#         container.setLayout(main_layout)
#         self.setCentralWidget(container)
#
#         # Initialize visibility
#         self.update_parameters_visibility()
#
#     def update_parameters_visibility(self):
#         method = self.method_combo.currentText()
#         self.tab_sift.setVisible(method == "sift")
#         self.tab_superpoint.setVisible(method == "superpoint")
#
#     def browse_file(self):
#         options = QFileDialog.Options()
#         file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть відео файл", "", "Video Files (*.mp4 *.avi)", options=options)
#         if file_path:
#             self.video_path_input.setText(file_path)
#
#     def browse_output_folder(self):
#         folder_path = QFileDialog.getExistingDirectory(self, "Виберіть папку для збереження результату")
#         if folder_path:
#             self.output_folder_input.setText(folder_path)
#
#     def start_stitching(self):
#         # Get parameters
#         method = self.method_combo.currentText()
#         transformation_type = self.transformation_combo.currentText()
#         frame_interval = self.frame_interval_input.value()
#         video_path = self.video_path_input.text()
#         output_folder = self.output_folder_input.text()
#
#         if not output_folder:
#             QMessageBox.critical(self, "Помилка", "Будь ласка, виберіть папку для збереження результату.")
#             return
#
#         if method == "sift":
#             stitcher = ImageStitcher(
#                 transformation_type=transformation_type,
#                 frame_interval=frame_interval,
#                 lowe_ratio=self.lowe_ratio_input.value(),
#                 ransac_reproj_thresh=self.ransac_thresh_input.value()
#             )
#         elif method == "superpoint":
#             stitcher = SuperPointStitcher(
#                 transformation_type=transformation_type,
#                 frame_interval=frame_interval,
#                 nms_radius=self.nms_radius_input.value(),
#                 keypoint_threshold=self.keypoint_threshold_input.value(),
#                 max_keypoints=self.max_keypoints_input.value()
#             )
#         else:
#             QMessageBox.critical(self, "Помилка", "Невідомий метод зшивання.")
#             return
#
#         # Start stitching
#         try:
#             self.progress_bar.setValue(0)
#             result = stitcher.stitch_video_frames(video_path)
#             self.progress_bar.setValue(50)
#             if result is not None:
#                 output_path = f"{output_folder}/stitched_result_final.png"
#                 stitcher.save_result(result, output_path)
#
#                 # Display result
#                 height, width, channel = result.shape
#                 max_width = self.result_image_label.width() - 20  # Padding for display
#                 max_height = self.result_image_label.height() - 20
#                 scale = min(max_width / width, max_height / height, 1.0)
#                 display_width = int(width * scale)
#                 display_height = int(height * scale)
#
#                 result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
#                 q_image = QImage(result_rgb.data, width, height, 3 * width, QImage.Format_RGB888)
#                 pixmap = QPixmap.fromImage(q_image).scaled(display_width, display_height, Qt.KeepAspectRatio)
#                 self.result_image_label.setPixmap(pixmap)
#                 self.result_image_label.setScaledContents(True)
#
#                 self.progress_bar.setValue(100)
#                 QMessageBox.information(self, "Успіх", f"Зшивання завершено. Результат збережено в {output_path}.")
#             else:
#                 self.progress_bar.setValue(0)
#                 QMessageBox.warning(self, "Попередження", "Зшивання завершено з помилкою.")
#         except Exception as e:
#             self.progress_bar.setValue(0)
#             QMessageBox.critical(self, "Помилка", f"Виникла помилка: {str(e)}")
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ex = StitchingApp()
#     ex.show()
#     sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QMessageBox, QTabWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt
from stitcher_sift import ImageStitcher
from stitcher_superpoint import SuperPointStitcher
import cv2

class StitchingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Stitching App")
        self.setWindowIcon(QIcon("icon.png"))  # Додайте шлях до вашої іконки
        self.resize(800, 600)

        # Main layout
        main_layout = QHBoxLayout()

        # Left-side layout for controls
        control_layout = QVBoxLayout()

        # Dropdown to select method
        self.method_label = QLabel("Метод зшивання:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["sift", "superpoint"])
        self.method_combo.currentTextChanged.connect(self.update_parameters_visibility)

        # Dropdown to select transformation type
        self.transformation_label = QLabel("Тип трансформації:")
        self.transformation_combo = QComboBox()
        self.transformation_combo.addItems(["homography", "affine"])

        # Batch normalization checkbox
        self.batch_normalization_label = QLabel("Використовувати пакетну нормалізацію:")
        self.batch_normalization_checkbox = QCheckBox()

        # SIFT parameters
        sift_layout = QFormLayout()
        self.lowe_ratio_input = QDoubleSpinBox()
        self.lowe_ratio_input.setRange(0.1, 1.0)
        self.lowe_ratio_input.setSingleStep(0.1)
        self.lowe_ratio_input.setValue(0.6)
        sift_layout.addRow("Lowe Ratio:", self.lowe_ratio_input)

        self.ransac_thresh_input = QDoubleSpinBox()
        self.ransac_thresh_input.setRange(0.1, 10.0)
        self.ransac_thresh_input.setSingleStep(0.5)
        self.ransac_thresh_input.setValue(2.0)
        sift_layout.addRow("RANSAC Threshold:", self.ransac_thresh_input)

        # SuperPoint parameters
        superpoint_layout = QFormLayout()
        self.nms_radius_input = QSpinBox()
        self.nms_radius_input.setRange(1, 20)
        self.nms_radius_input.setValue(4)
        superpoint_layout.addRow("NMS Radius:", self.nms_radius_input)

        self.keypoint_threshold_input = QDoubleSpinBox()
        self.keypoint_threshold_input.setRange(0.0001, 0.1)
        self.keypoint_threshold_input.setSingleStep(0.0001)
        self.keypoint_threshold_input.setValue(0.01)
        superpoint_layout.addRow("Keypoint Threshold:", self.keypoint_threshold_input)

        self.max_keypoints_input = QSpinBox()
        self.max_keypoints_input.setRange(100, 5000)
        self.max_keypoints_input.setValue(1024)
        superpoint_layout.addRow("Max Keypoints:", self.max_keypoints_input)

        # Frame interval parameter
        self.frame_interval_input = QSpinBox()
        self.frame_interval_input.setRange(1, 100)
        self.frame_interval_input.setValue(30)

        # Batch size parameter
        self.batch_size_label = QLabel("Розмір пакету:")
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setRange(1, 10)
        self.batch_size_input.setValue(2)

        # Tab widget for parameters
        self.tab_widget = QTabWidget()
        self.tab_sift = QWidget()
        self.tab_superpoint = QWidget()
        self.tab_sift.setLayout(sift_layout)
        self.tab_superpoint.setLayout(superpoint_layout)

        self.tab_widget.addTab(self.tab_sift, "SIFT Parameters")
        self.tab_widget.addTab(self.tab_superpoint, "SuperPoint Parameters")

        # Video file selection
        self.video_path_label = QLabel("Файл відео:")
        self.video_path_input = QLineEdit()
        self.browse_button = QPushButton("Огляд")
        self.browse_button.clicked.connect(self.browse_file)

        # Output folder selection
        self.output_folder_label = QLabel("Папка для збереження результату:")
        self.output_folder_input = QLineEdit()
        self.output_browse_button = QPushButton("Огляд")
        self.output_browse_button.clicked.connect(self.browse_output_folder)

        # Start stitching button
        self.stitch_button = QPushButton("Запустити зшивання")
        self.stitch_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.stitch_button.clicked.connect(self.start_stitching)

        # Add widgets to control layout
        control_layout.addWidget(self.method_label)
        control_layout.addWidget(self.method_combo)
        control_layout.addWidget(self.transformation_label)
        control_layout.addWidget(self.transformation_combo)
        control_layout.addWidget(self.batch_normalization_label)
        control_layout.addWidget(self.batch_normalization_checkbox)
        control_layout.addWidget(QLabel("Інтервал кадрів:"))
        control_layout.addWidget(self.frame_interval_input)
        control_layout.addWidget(self.batch_size_label)
        control_layout.addWidget(self.batch_size_input)
        control_layout.addWidget(self.tab_widget)
        control_layout.addWidget(self.video_path_label)
        control_layout.addWidget(self.video_path_input)
        control_layout.addWidget(self.browse_button)
        control_layout.addWidget(self.output_folder_label)
        control_layout.addWidget(self.output_folder_input)
        control_layout.addWidget(self.output_browse_button)
        control_layout.addWidget(self.stitch_button)

        # Right-side layout for image display
        image_layout = QVBoxLayout()
        self.result_image_label = QLabel()
        self.result_image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.result_image_label)

        # Add layouts to main layout
        main_layout.addLayout(control_layout, 1)
        main_layout.addLayout(image_layout, 2)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize visibility
        self.update_parameters_visibility()

    def update_parameters_visibility(self):
        method = self.method_combo.currentText()
        self.tab_sift.setVisible(method == "sift")
        self.tab_superpoint.setVisible(method == "superpoint")

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть відео файл", "", "Video Files (*.mp4 *.mov)", options=options)
        if file_path:
            self.video_path_input.setText(file_path)

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Виберіть папку для збереження результату")
        if folder_path:
            self.output_folder_input.setText(folder_path)

    def start_stitching(self):
        # Get parameters
        method = self.method_combo.currentText()
        transformation_type = self.transformation_combo.currentText()
        frame_interval = self.frame_interval_input.value()
        batch_size = self.batch_size_input.value()
        use_batch_norm = self.batch_normalization_checkbox.isChecked()
        video_path = self.video_path_input.text()
        output_folder = self.output_folder_input.text()

        if not output_folder:
            QMessageBox.critical(self, "Помилка", "Будь ласка, виберіть папку для збереження результату.")
            return

        if method == "sift":
            stitcher = ImageStitcher(
                transformation_type=transformation_type,
                frame_interval=frame_interval
            )
        elif method == "superpoint":
            stitcher = SuperPointStitcher(
                transformation_type=transformation_type,
                frame_interval=frame_interval,
                batch_size=batch_size
            )
        else:
            QMessageBox.critical(self, "Помилка", "Невідомий метод зшивання.")
            return

        # Start stitching
        try:
            result = stitcher.stitch_video_frames(video_path)
            if result is not None:
                output_path = f"{output_folder}/stitched_result_final.png"
                stitcher.save_result(result, output_path)

                # Display result
                height, width, channel = result.shape
                max_width = self.result_image_label.width() - 20  # Padding for display
                max_height = self.result_image_label.height() - 20
                scale = min(max_width / width, max_height / height, 1.0)
                display_width = int(width * scale)
                display_height = int(height * scale)

                result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                q_image = QImage(result_rgb.data, width, height, 3 * width, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image).scaled(display_width, display_height, Qt.KeepAspectRatio)
                self.result_image_label.setPixmap(pixmap)
                self.result_image_label.setScaledContents(True)

                QMessageBox.information(self, "Успіх", f"Зшивання завершено. Результат збережено в {output_path}.")
            else:
                QMessageBox.warning(self, "Попередження", "Зшивання завершено з помилкою.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Виникла помилка: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = StitchingApp()
    ex.show()
    sys.exit(app.exec_())

