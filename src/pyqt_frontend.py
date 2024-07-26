import sys
from PySide6.QtCore import * 
from PySide6.QtWidgets import * 
from PySide6.QtGui import *
from AudioBuffer import AudioBuffer
from process_funcs import *
import numpy as np
import matplotlib.pyplot as plt
from music21 import *
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
        self.buffer = AudioBuffer(name="buffer", 
                         frames_per_buffer=4096,
                         wav_file='audio_files\moonlight_sonata.wav',
                         process_func=play_wav_data,
                         process_func_args=(),
                         calc_chroma=True, 
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
        except Exception as e:
            print("Detected interrupt")
            self.buffer.stop()
            self.buffer.join()

    @Slot(int)
    def set_playback_rate(self, playback_rate):
        self.buffer.playback_rate = playback_rate

    @Slot()
    def stop(self):
        if self.isRunning():
            self.buffer.stop()

    @Slot()
    def pause(self):
        self.buffer.pause()

    @Slot()
    def unpause(self):
        self.buffer.unpause()

    @Slot(int)
    def get_last_chroma(self, num_features):
        return self.buffer.get_last_chroma(num_features)


class Slider(QSlider):
    def __init__(self, val:float, name: str, minVal:float, align: int,
                 maxVal:float, calc:int, thread:WorkerThread):
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

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chroma)

        self.timer.start(100)


    @Slot()
    def start_task(self):
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
        mus = converter.parse("audio_files\ode_to_joy.musicxml")
        mus.write('xml.png', 'sheet.png')

        pixmap = QPixmap("sheet-1.png")
        pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio)
        self.sheet_display.setPixmap(pixmap)

    @Slot()
    def update_chroma(self):
        num_features = 200
        chroma = self.thread.get_last_chroma(num_features)
        chroma = np.sum(chroma, axis=0)
        chroma = chroma.reshape((12, -1))
        chroma = np.flip(chroma, axis=0)
        img_data = np.zeros((12, num_features))

        if chroma.size > 0:
            img_data[:, -chroma.shape[-1]:] = chroma

        image_filepath = 'chroma_buffer.png'
        plt.imsave(image_filepath, img_data, cmap='plasma')

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