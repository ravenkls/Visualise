from pydub import AudioSegment
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtMultimedia import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from visualisefft import VisualiseFFT
from visualisefrequency import VisualiseFrequency
from visualisewaves import VisualiseWaves
import argparse
import sys


class AudioVisualiser(QtWidgets.QWidget):

    def __init__(self, audio_file, visualiser, polar=False):
        super().__init__()
        self.setWindowTitle(audio_file)
        song = AudioSegment.from_mp3(audio_file)
        self.playing = False
        song = song.set_channels(1)

        content = QMediaContent(QtCore.QUrl(audio_file))
        self.player = QMediaPlayer()

        figure = Figure()
        canvas = FigureCanvas(figure)
        canvas.setParent(self)

        self.vis = visualiser(song, canvas, self.player, polar=polar)
        
        self.player.setMedia(content)
        self.player.mediaStatusChanged.connect(self.start)

    def start(self, status):
        if self.playing:
            self.player.stop()
        elif status == self.player.LoadedMedia:
            self.player.play()
            self.vis.start()
        elif status == self.player.BufferedMedia:
            self.playing = True

    def closeEvent(self, event):
        self.player.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('audio', help='The audio file to visualise')
    parser.add_argument('-m', '--mode', help='The visualisation mode',
                        default='frequency', choices=['waves', 'frequency', 'fft'])
    parser.add_argument('-p', '--polar', help='Plot as a polar graph', action='store_true', default=False)
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    mode = {'waves': VisualiseWaves, 'frequency': VisualiseFrequency, 'fft': VisualiseFFT}[args.mode]
    window = AudioVisualiser(args.audio, mode, polar=args.polar)
    window.setFixedSize(640, 480)
    window.show()
sys.exit(app.exec_())
