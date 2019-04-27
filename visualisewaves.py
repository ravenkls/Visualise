import matplotlib.pyplot as plt
from PyQt5 import QtCore
import numpy as np
import time
import math



class VisualiseWaves(QtCore.QThread):

    def __init__(self, song, canvas, player):
        super().__init__()
        self.canvas = canvas
        self.figure = self.canvas.figure
        self.player = player
        self.samples = song.get_array_of_samples()
        self.song = song

    def run(self):
        self.figure.patch.set_facecolor((0, 0, 0))
        ax1 = self.figure.add_subplot(1,1,1)
        ax1.set_facecolor((0, 0, 0))
        
        interval = 0.05
        
        for timestamp in range(0, math.ceil(self.song.duration_seconds/interval)):
            start = time.time()
            
            timestamp *= interval
            sample_count = int(self.song.frame_rate * interval)
            start_index = int((self.player.position()/1000) * self.song.frame_rate)
            v_sample = self.samples[start_index:start_index+sample_count]

            ax1.clear()
            if ax1.lines:
                ax1.lines[0].set_data(range(len(v_sample)), v_sample)
            else:
                ax1.plot(range(len(v_sample)), v_sample, color='r')
            self.canvas.draw()
            plt.pause(0.001)
            time.sleep(max(interval - time.time() + start, 0))
