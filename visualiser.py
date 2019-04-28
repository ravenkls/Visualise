from pydub import AudioSegment
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtMultimedia import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from visualisefft import VisualiseFFT
from visualisewaves import VisualiseWaves
import argparse
import sys

import matplotlib.pyplot as plt


class AudioVisualiser(QtWidgets.QWidget):

    def __init__(self, audio_file):
        super().__init__()
        self.setWindowTitle(audio_file)
        self.fft = VisualiseFFT(audio_file, 'hp_video.mp4', polar=True, background='background.jpg')
        
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.fft.progress.connect(self.show_progress)
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setRange(0, self.fft.song.duration_seconds)

        self.layout().addWidget(self.progress)

        self.fft.start()
    
    def show_progress(self, timestamp):
        if timestamp % 1 == 0:
            self.progress.setValue(timestamp)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AudioVisualiser('hp.mp3')
    window.show()

    sys.exit(app.exec_())
