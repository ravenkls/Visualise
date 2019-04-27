import matplotlib.pyplot as plt
from PyQt5 import QtCore
import numpy as np
import time
import math


class VisualiseFrequency(QtCore.QThread):

    def __init__(self, song, canvas, player):
        super().__init__()
        self.canvas = canvas
        self.figure = self.canvas.figure
        self.player = player
        self.samples = np.array(song.get_array_of_samples())
        self.song = song

    def run(self):
        self.figure.patch.set_facecolor((0, 0, 0))
        ax1 = self.figure.add_subplot(1,1,1)
        ax1.set_facecolor((0, 0, 0))
        
        interval = 0.05
        bars_n = 60

        frequency_range = 1
        
        bars = np.zeros(bars_n)
        max_sample = self.samples.max()
        for timestamp in range(0, math.ceil(self.song.duration_seconds/interval)):
            start = time.time()
            
            timestamp *= interval
            sample_count = int(self.song.frame_rate * interval)
            start_index = int((self.player.position()/1000) * self.song.frame_rate)
            v_sample = self.samples[start_index:start_index+sample_count]

            fourier = np.fft.fft(v_sample)
            freq = np.fft.fftfreq(fourier.size, d=interval)
            amps = 2/v_sample.size * np.abs(fourier)
            data = np.array([freq, amps]).T
            
            bar_width_range = frequency_range / bars_n
            bars_samples = np.array([])

            if not data.size:
                time.sleep(max(interval - time.time() + start, 0))
                continue
            
            for f in np.arange(0, frequency_range, bar_width_range):
                amps = np.array(data)
                amps = amps[(f-bar_width_range<amps[:,0]) & (amps[:,0]<f)]
                if not amps.size:
                    bars_samples = np.append(bars_samples, 0)
                else:
                    bars_samples = np.append(bars_samples, amps.max())

            for n, amp in enumerate(bars_samples):
                if bars[n] > 0 and amp < bars[n]:
                        bars[n] -= bars[n] / 3
                        if bars[n] < 1:
                            bars[n] = 0
                else:
                    bars[n] = amp
                    if bars[n] < 1:
                            bars[n] = 0
            ax1.clear()
            if ax1.lines:
                ax1.lines[0].set_data(range(len(bars)), bars)
            else:
                ax1.plot(range(len(bars)), bars, color='r')
            ax1.set_ylim(top=max_sample, bottom=0)
            ax1.fill_between(range(len(bars)), bars, color='#c60303')
            self.canvas.draw()
            plt.pause(0.001)
            time.sleep(max(interval - time.time() + start, 0))
