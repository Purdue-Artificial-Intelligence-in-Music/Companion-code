import sys
import random
from PySide6.QtCore import * 
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from AudioBuffer import AudioBuffer
from process_funcs import *
import numpy as np


class WorkerThread(QThread):
    finished_signal = Signal()
    playback_rate = Signal(int)


    def __init__(self):
        super().__init__()
        self.buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=1024,
                         wav_file='audio_files\cello_suite1_cello.wav',
                         process_func=play_wav_data,
                         process_func_args=(),
                         calc_chroma=False, 
                         calc_beats=False,
                         kill_after_finished=True,
                         playback_rate=1.0,
                         sample_rate=None,
                         dtype=np.float32,
                         channels=1,
                         debug_prints=True)

    def run(self):
        self.buffer.start()
        try:
            while not self.buffer.stop_request:
                QThread.sleep(0.1)
                self.finished_signal.emit()  # Emit finished signal when done
        except Exception as e:
            print("Detected interrupt")
            self.buffer.stop()
            self.buffer.join()

    @Slot(int)
    def set_playback_rate(self, playback_rate):
        self.buffer.playback_rate = playback_rate

    @Slot()
    def stop(self):
        self.buffer.stop()

    @Slot()
    def pause(self):
        self.buffer.pause()

    @Slot()
    def unpause(self):
        self.buffer.unpause()


class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.speed = 1

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.pause_button = QPushButton("Pause")
        self.unpause_button = QPushButton("Unpause")

        self.speed_text = QLabel(f"Speed: {self.speed}", alignment=Qt.AlignCenter)

        self.speed_slider = QSlider(orientation=Qt.Orientation.Horizontal, )
        self.speed_slider.setValue(self.speed * 100)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(200)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.speed_text)
        self.layout.addWidget(self.speed_slider)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.unpause_button)

        self.speed_slider.sliderMoved.connect(self.set_speed)
        self.start_button.clicked.connect(self.start_task)
        self.stop_button.clicked.connect(self.stop_task)
        self.pause_button.clicked.connect(self.pause_task)
        self.unpause_button.clicked.connect(self.unpause_task)

        self.thread = WorkerThread()

    @Slot()
    def set_speed(self):
        self.speed = self.speed_slider.value() / 100
        self.speed_text.setText(f"Speed: {self.speed}")
        self.thread.set_playback_rate(self.speed)

    @Slot()
    def start_task(self):
        self.thread.start()

    @Slot()
    def stop_task(self):
        self.thread.stop()
        self.close()

    @Slot()
    def pause_task(self):
        self.thread.pause()

    @Slot()
    def unpause_task(self):
        self.thread.unpause()


if __name__ == "__main__":
    app = QApplication([])

    widget = Demo()
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())