import sys
from PySide6.QtCore import * 
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from AudioPlayer import AudioPlayer
from AudioBuffer import AudioBuffer
import numpy as np
import matplotlib.pyplot as plt
from music21 import *
import librosa
from Synchronizer import Synchronizer
import time
env = environment.UserSettings()
env['musescoreDirectPNGPath'] = env['musicxmlPath']

#Download musescore without hub from https://musescore.org/en
#Run python -m music21.configure in terminal
#Other options to look at are using the musescore module or lilypond

from audioflux.display import fill_spec

#Link to music21 docs https://web.archive.org/web/20211127032016/http://web.mit.edu/music21/doc

class WorkerThread(QThread):
    finished_signal = Signal()
    playback_rate = Signal(int)

    def __init__(self):
        super().__init__()

        self.sync = Synchronizer(reference='data/bach/synthesized/track0.wav',
                                 accompaniment='data/bach/synthesized/track1.wav',
                                 source='data/bach/live/constant_tempo.wav',
                                 Kp=0.5,
                                 Ki=0.001,
                                 Kd=0.05,
                                 sample_rate=16000,
                                 win_length=4096,
                                 hop_length=1024,
                                 c=20,
                                 max_run_count=3,
                                 diag_weight=0.5,
                                 channels=1,
                                 frames_per_buffer=1024)

    def run(self):
        self.sync.start()
        # wait until the synchronizer is active
        while not self.sync.is_active():
            QThread.sleep(0.01)

        try:
            while self.sync.is_active():
                QThread.sleep(0.1)
        except Exception as e:
            print("Detected interrupt")
            self.stop()

    @Slot(int)
    def set_playback_rate(self, playback_rate):
        self.sync.player.playback_rate = playback_rate

    @Slot()
    def stop(self):
        self.sync.stop()

    @Slot()
    def pause(self):
        self.sync.pause()

    @Slot()
    def unpause(self):
        self.sync.unpause()

    @Slot()
    def get_next_chroma(self):
        chroma = self.sync.score_follower.otw.live[..., self.sync.score_follower.otw.t]
        return chroma
    
    @Slot()
    def get_chroma(self):
        return self.sync.score_follower.otw.live


class Slider(QSlider):
    def __init__(self, val:float, name: str, minVal:float, align: int,
                 maxVal:float, calc:int, thread: WorkerThread):
        super(Slider, self).__init__()
        self.val = val
        self.calc = calc
        self.name = name
        self.calc = calc
        self.setValue(self.calc*self.val)
        self.setMinimum(minVal)
        self.setMaximum(maxVal)
        self.label = QLabel(f"{self.name}: {self.val}", alignment=align)
        self.thread = thread
        
    @Slot()
    def set_val(self):
        self.val = self.value() / self.calc
        self.label.setText(f"{self.name}: {self.val}")
        self.thread.set_playback_rate(self.val) 

class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()

        self.thread = WorkerThread()
        self.speed = Slider(val=1, thread=self.thread, name="Speed", minVal=0, maxVal=200, calc=100, align=Qt.AlignCenter)
        self.speed.setOrientation(Qt.Orientation.Horizontal)
        self.speed.valueChanged.connect(self.speed.set_val)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.pause_button = QPushButton("Pause") 
        self.unpause_button = QPushButton("Resume")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.speed.label)
        self.layout.addWidget(self.speed)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.unpause_button)

        self.start_button.clicked.connect(self.start_task)
        self.stop_button.clicked.connect(self.stop_task)
        self.pause_button.clicked.connect(self.pause_task)
        self.unpause_button.clicked.connect(self.unpause_task)

        self.chroma_display = QLabel(alignment=Qt.AlignCenter)
        self.sheet_display = QLabel(alignment=Qt.AlignCenter)

        self.layout.addWidget(self.chroma_display)
        self.layout.addWidget(self.sheet_display)
        self.set_sheet()

        self.img_data = np.zeros_like(self.thread.get_chroma())

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chroma)

        self.timer.start(100)

    @Slot()
    def start_task(self):
        self.timer.start(1024 / self.thread.sync.sample_rate * 1000)
        self.thread.start()

    @Slot()
    def stop_task(self):
        self.thread.stop()
        self.close()

    @Slot()
    def pause_task(self):
        if self.thread.isRunning():
            self.thread.pause()
            #Pauses choma display
            self.timer.timeout.disconnect(self.update_chroma)

    @Slot()
    def unpause_task(self):
        if self.thread.isRunning():
            self.thread.unpause()
            #Unpauses choma display
            self.timer.timeout.connect(self.update_chroma)

    @Slot()
    def set_sheet(self):
        #readfile = self.thread.buffer.wav_file.split('.')[0]
        #xml_file = readfile + ".musicxl"
        mus = converter.parse("scores\ode_to_joy.musicxml")
        mus.write('xml.png', 'sheet.png')

        pixmap = QPixmap("sheet-1.png")
        pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio)
        self.sheet_display.setPixmap(pixmap)

    @Slot()
    def update_chroma(self):
        chroma = self.thread.get_next_chroma()
        chroma = chroma.reshape((12, -1))
        chroma = np.flip(chroma, axis=0)

        # self.img_data = np.concatenate((self.img_data[:, 1:], chroma), axis=1)

        chromagram = self.thread.get_chroma()
        image_filepath = 'chroma_buffer.png'
        plt.imsave(image_filepath, chromagram, cmap='plasma')

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