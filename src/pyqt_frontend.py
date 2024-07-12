import sys
from PySide6.QtCore import * 
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from AudioPlayer import AudioPlayer
import numpy as np
import matplotlib.pyplot as plt
from features import audio_to_np_cens

class WorkerThread(QThread):

    def __init__(self):
        super().__init__()
        self.player = AudioPlayer('audio/Air_on_the_G_String/track0.wav')
        self.playback_rate = Signal(int)
        print(self.player.audio.shape)
        self.chroma_cens = audio_to_np_cens(self.player.audio.reshape((-1,)), sr=self.player.sample_rate, n_fft=1024, hop_len=1024)
        print(self.chroma_cens.shape)
        self.chroma_index = 0

    def run(self):
        self.player.start()
        try:
            while self.player.is_active():
                QThread.sleep(0.1)
        except Exception as e:
            print("Detected interrupt")
            self.player.stop()
            self.player.join()

    @Slot(int)
    def set_playback_rate(self, playback_rate):
        self.player.playback_rate = playback_rate

    @Slot()
    def stop(self):
        self.player.stop()

    @Slot()
    def pause(self):
        self.player.pause()

    @Slot()
    def unpause(self):
        self.player.unpause()

    @Slot()
    def get_next_chroma(self):
        chroma = self.chroma_cens[:, self.chroma_index]
        self.chroma_index += 1
        return chroma


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

        self.chroma_display = QLabel(alignment=Qt.AlignCenter)

        self.layout.addWidget(self.chroma_display)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chroma)

        self.img_data = np.zeros((12, 200))

    @Slot()
    def set_speed(self):
        self.speed = self.speed_slider.value() / 100
        self.speed_text.setText(f"Speed: {self.speed}")
        self.thread.set_playback_rate(self.speed)

    @Slot()
    def start_task(self):
        self.timer.start(1024 / self.thread.player.sample_rate * 1000)
        self.thread.start()

    @Slot()
    def stop_task(self):
        self.thread.stop()
        self.close()

    @Slot()
    def pause_task(self):
        self.timer.stop()
        self.thread.pause()

    @Slot()
    def unpause_task(self):
        self.timer.start()
        self.thread.unpause()

    @Slot()
    def update_chroma(self):
        chroma = self.thread.get_next_chroma()
        chroma = chroma.reshape((12, -1))

        self.img_data = np.concatenate((self.img_data[:, 1:], chroma), axis=1)

        image_filepath = 'chroma_buffer.png'
        plt.imsave(image_filepath, self.img_data, cmap='plasma')

        # Load the image using QPixmap
        pixmap = QPixmap(image_filepath)
        pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio)

        self.chroma_display.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication([])

    widget = Demo()
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())