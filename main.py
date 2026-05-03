import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QFileDialog, QProgressBar, QGroupBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from src.whisper_recognizer import WhisperRecognizer
from src.subtitle_generator import SubtitleGenerator, SubtitleSegment


class TranscriptionThread(QThread):
    progress_updated = pyqtSignal(float)
    status_updated = pyqtSignal(str)
    transcription_finished = pyqtSignal(dict)

    def __init__(self, audio_path, language, model_name):
        super().__init__()
        self.audio_path = audio_path
        self.language = language
        self.model_name = model_name

    def run(self):
        try:
            self.status_updated.emit("正在加载模型...")
            self.progress_updated.emit(5)

            recognizer = WhisperRecognizer(model_name=self.model_name)

            self.status_updated.emit("正在转录音频...")
            self.progress_updated.emit(10)

            result = recognizer.transcribe(
                self.audio_path,
                language=self.language
            )

            self.progress_updated.emit(100)
            self.status_updated.emit("转录完成")
            self.transcription_finished.emit(result)

        except Exception as e:
            self.status_updated.emit(f"错误: {str(e)}")
            self.transcription_finished.emit({"success": False, "error": str(e)})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.segments = []
        self.subtitle_generator = SubtitleGenerator()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("本地字幕生成工具 - Offline Subtitle Generator")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        title_label = QLabel("🎬 本地音视频字幕自动生成工具")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        file_group = QGroupBox("📁 文件选择")
        file_layout = QHBoxLayout()

        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("选择音频或视频文件...")
        file_layout.addWidget(self.file_input)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        settings_group = QGroupBox("⚙️ 设置")
        settings_layout = QHBoxLayout()

        settings_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("small")
        settings_layout.addWidget(self.model_combo)

        settings_layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "意大利文", "葡萄牙文", "俄文"
        ])
        self.language_combo.setCurrentText("中文")
        settings_layout.addWidget(self.language_combo)

        settings_layout.addWidget(QLabel("线程数:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(16)
        self.threads_spin.setValue(4)
        settings_layout.addWidget(self.threads_spin)

        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        self.start_btn = QPushButton("🎯 开始生成字幕")
        self.start_btn.clicked.connect(self.start_transcription)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        main_layout.addWidget(self.start_btn)

        self.status_label = QLabel("状态: 就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        preview_group = QGroupBox("📝 字幕预览")
        preview_layout = QVBoxLayout()

        self.subtitle_table = QTableWidget()
        self.subtitle_table.setColumnCount(4)
        self.subtitle_table.setHorizontalHeaderLabels(["序号", "开始时间", "结束时间", "文本内容"])
        self.subtitle_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.subtitle_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.subtitle_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.subtitle_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self.subtitle_table)

        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        export_group = QGroupBox("💾 导出设置")
        export_layout = QHBoxLayout()

        export_layout.addWidget(QLabel("格式:"))
        self.format_label = QLabel("SRT (视频字幕)")
        export_layout.addWidget(self.format_label)

        export_layout.addWidget(QLabel("输出路径:"))
        self.output_input = QLineEdit()
        export_layout.addWidget(self.output_input)

        self.export_btn = QPushButton("导出字幕文件")
        self.export_btn.clicked.connect(self.export_subtitle)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)

        export_layout.addStretch()
        export_group.setLayout(export_layout)
        main_layout.addWidget(export_group)

        info_label = QLabel("💡 提示: 完全本地运行，无需联网，保护隐私 | 支持 MP3, WAV, M4A, MP4, MKV, AVI 等格式")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666666; padding: 5px;")
        main_layout.addWidget(info_label)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音视频文件",
            "",
            "音视频文件 (*.mp3 *.wav *.m4a *.flac *.ogg *.mp4 *.mkv *.avi *.mov *.wmv);;所有文件 (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_input.setText(file_path)

            base_name = os.path.splitext(file_path)[0]
            default_output = f"{base_name}.srt"
            self.output_input.setText(default_output)

    def start_transcription(self):
        if not self.current_file:
            QMessageBox.warning(self, "警告", "请先选择音视频文件！")
            return

        if not os.path.exists(self.current_file):
            QMessageBox.warning(self, "错误", "文件不存在！")
            return

        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("状态: 准备中...")

        language_map = {
            "中文": "zh", "英文": "en", "日文": "ja", "韩文": "ko",
            "法文": "fr", "德文": "de", "西班牙文": "es",
            "意大利文": "it", "葡萄牙文": "pt", "俄文": "ru"
        }
        language = language_map.get(self.language_combo.currentText(), "zh")
        model_name = self.model_combo.currentText()

        self.thread = TranscriptionThread(self.current_file, language, model_name)
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.status_updated.connect(self.update_status)
        self.thread.transcription_finished.connect(self.on_transcription_finished)
        self.thread.start()

    @pyqtSlot(float)
    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

    @pyqtSlot(str)
    def update_status(self, status):
        self.status_label.setText(f"状态: {status}")

    @pyqtSlot(dict)
    def on_transcription_finished(self, result):
        self.start_btn.setEnabled(True)

        if result.get("success", False):
            self.segments = result.get("segments", [])
            self.display_segments()
            self.export_btn.setEnabled(True)
            QMessageBox.information(self, "成功", f"转录完成！共识别 {len(self.segments)} 个字幕段")
        else:
            error_msg = result.get("error", "未知错误")
            QMessageBox.critical(self, "错误", f"转录失败: {error_msg}")

    def display_segments(self):
        self.subtitle_table.setRowCount(0)

        for seg in self.segments:
            row = self.subtitle_table.rowCount()
            self.subtitle_table.insertRow(row)

            self.subtitle_table.setItem(row, 0, QTableWidgetItem(str(seg.index)))

            start_time = self.format_time_display(seg.start_ms)
            end_time = self.format_time_display(seg.end_ms)
            self.subtitle_table.setItem(row, 1, QTableWidgetItem(start_time))
            self.subtitle_table.setItem(row, 2, QTableWidgetItem(end_time))
            self.subtitle_table.setItem(row, 3, QTableWidgetItem(seg.text))

    def format_time_display(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        s = seconds % 60
        m = minutes % 60
        return f"{hours:02d}:{m:02d}:{s:02d},{ms % 1000:03d}"

    def export_subtitle(self):
        if not self.segments:
            QMessageBox.warning(self, "警告", "没有可导出的字幕！")
            return

        output_path = self.output_input.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请指定输出文件路径！")
            return

        if self.subtitle_generator.save_srt(self.segments, output_path):
            QMessageBox.information(self, "成功", f"字幕已保存到:\n{output_path}")
        else:
            QMessageBox.critical(self, "错误", "保存字幕文件失败！")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
