import matplotlib.pyplot as plt
from PyQt5 import QtCore
import numpy as np
import time
import math



class VisualiseWaves(QtCore.QThread):

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

        for timestamp in range(0, math.ceil(self.song.duration_seconds/interval)):
            start = time.time()
            
            timestamp *= interval
            sample_count = int(self.song.frame_rate * interval)
            start_index = int((self.player.position()/1000) * self.song.frame_rate)
            v_sample = self.samples[start_index:start_index+sample_count]

            ax1.clear()
            ax1.grid(False)
            ax1.set_yticklabels([])
            
            thetas = np.arange(0, math.pi*2, (2*math.pi)/len(v_sample))
            rs = v_sample
            if self.polar:
                thetas = np.append(thetas, 0)
                rs = np.append(rs, rs[0]) + abs(self.samples.min())*1.5
            if ax1.lines:
                ax1.lines[0].set_data(thetas, rs)
            else:
                ax1.plot(thetas, rs, color='r')
            self.canvas.draw()
            plt.pause(0.001)
            time.sleep(max(interval - time.time() + start, 0))
