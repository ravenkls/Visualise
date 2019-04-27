import matplotlib.pyplot as plt
from PyQt5 import QtCore
import numpy as np
import time
import math



class VisualiseFrequency(QtCore.QThread):

    def __init__(self, song, canvas, player, *, polar=False):
        super().__init__()
        self.canvas = canvas
        self.polar = polar
        self.figure = self.canvas.figure
        self.player = player
        self.samples = np.array(song.get_array_of_samples())
        self.song = song

    def run(self):
        self.figure.patch.set_facecolor((0, 0, 0))
        ax1 = self.figure.add_subplot(111, polar=self.polar)
        ax1.set_facecolor((0, 0, 0))
        
        interval = 0.05
        bars_n = 60
        max_bar_height = 35
        frequency_range = 0.3
        
        bars = [0]*bars_n
        max_sample = self.samples.max()
        for timestamp in range(0, math.ceil(self.song.duration_seconds/interval)):
            start = time.time()
            
            timestamp *= interval
            sample_count = int(self.song.frame_rate * interval)
            start_index = int((self.player.position()/1000) * self.song.frame_rate)
            v_sample = self.samples[start_index:start_index+sample_count]

            zero_crossings = np.where(np.diff(np.sign(v_sample)))[0]
            data = []
            for i in range(len(zero_crossings)-1):
                x1 = zero_crossings[i]
                x2 = zero_crossings[i+1]
                diff = abs(x1 - x2)
                frequency = (diff / len(v_sample))
                amp = max(max(v_sample[x1:x2]), abs(min(v_sample[x1:x2])))
                data.append((frequency, amp))
            
            
            bar_width_range = frequency_range / bars_n
            bars_samples = []

            if not data:
                time.sleep(max(interval - time.time() + start, 0))
                continue
            
            for f in np.arange(0, frequency_range, bar_width_range):
                amps = [x[1] for x in data if f-bar_width_range<x[0]<f]
                if not amps:
                    bars_samples.append(0)
                else:
                    bars_samples.append(max(amps))

            highest_amp = 18000
            step = highest_amp // max_bar_height
            if step:
                for n, amp in enumerate(bars_samples):
                    if bars[n] > 0 and amp // step < bars[n]:
                            bars[n] -= bars[n] / 3
                            if bars[n] < 1:
                                bars[n] = 0
                    else:
                        bars[n] = amp // step
                        if bars[n] < 1:
                                bars[n] = 0
            else:
                bars = [0]*bars

            ax1.clear()
            ax1.grid(False)
            ax1.set_yticklabels([])
            
            thetas = np.arange(0, math.pi*2, (2*math.pi)/len(bars))
            rs = bars
            if self.polar:
                thetas = np.append(thetas, 0)
                rs = np.append(rs, rs[0]) + 20
                
            if ax1.lines:
                ax1.lines[0].set_data(thetas, rs)
            else:
                ax1.plot(thetas, rs, color='r')
            ax1.set_ylim(top=100, bottom=0)
            ax1.fill_between(thetas, rs, color='#c60303')
            self.canvas.draw()
            plt.pause(0.001)
            time.sleep(max(interval - time.time() + start, 0))
