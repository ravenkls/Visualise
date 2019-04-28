import matplotlib.pyplot as plt
from progressbar import progressbar
import cv2
from PyQt5 import QtCore
from pydub import AudioSegment
import numpy as np
import time
import math
import os
import io
import pdb
import subprocess
import itertools
from PIL import Image, ImageFilter, ImageSequence


class VisualiseFFT(QtCore.QThread):

    progress = QtCore.pyqtSignal(float)

    def __init__(self, audio_file, video_output, **options):
        super().__init__()
        self.audio_file = audio_file
        self.video_output = video_output
        self.song = AudioSegment.from_file(self.audio_file)
        self.song = self.song.set_channels(1)
        self.samples = np.array(self.song.get_array_of_samples())
        self.max_sample = self.samples.max()
        self.polar = options.get('polar', False)
        self.interval = options.get('interval', 0.05)
        self.resolution = options.get('resolution', 60)
        self.amplify_factor = options.get('amplify_factor', 4)
        self.stroke_colour = options.get('stroke_colour', (27, 142, 123))
        self.fill_colour = options.get('fill_colour', (25, 214, 183))
        self.background_file = options.get('background', None)
        self.background_zoom = options.get('background_zoom', 1.1)
        self.particles_file = options.get('particles', 'particles.gif')
        self.particles_image = Image.open(self.particles_file)
        self.particle_frames = itertools.cycle(ImageSequence.Iterator(self.particles_image))
        if self.background_file:
            self.background_image = Image.open(self.background_file).filter(ImageFilter.BLUR)
        else:
            self.background_image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

    def zoom_background(self, image, factor):
        enlarged = image.resize((int(image.width*factor), int(image.height*factor)))
        left = int((factor - 1)/2 * image.width)
        top = int((factor - 1)/2 * image.height)
        right = enlarged.width - left
        bottom = enlarged.height - top
        cropped = enlarged.crop((left, top, right, bottom))
        cropped.resize((image.width, image.height))
        return cropped


    def run(self):
        self.figure = plt.figure(figsize=(19.2, 10.8), dpi=100)
        ax = self.figure.add_subplot(111, polar=self.polar)

        matplotlib_stroke = [colour/255 for colour in self.stroke_colour]
        matplotlib_fill = [colour/255 for colour in self.fill_colour]

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter('tmp.mp4', fourcc, 1/self.interval, (1920, 1080))
        
        est_mean = np.mean(self.samples)
        est_std = 3 * np.std(self.samples) / np.sqrt(2)
        bass_frequency = int(round((est_std - est_mean) * 0.05))

        bars = np.zeros(self.resolution)
        sample_count = int(self.song.frame_rate * self.interval)

        current_background_zoom = 0
        for timestamp in np.arange(0, self.song.duration, self.interval):
            
            sample_index = int(timestamp * self.song.frame_rate)
            v_sample = self.samples[sample_index:sample_index+sample_count]

            fourier = np.fft.fft(v_sample)
            freq = np.fft.fftfreq(fourier.size, d=self.interval)
            amps = 2/v_sample.size * np.abs(fourier)
            data = np.array([freq, amps]).T

            bar_width_range = 1 / self.resolution
            bars_samples = np.array([])
            bass_amplitude = data[data[:,0]<bass_frequency].max()

            for f in np.arange(0, 1, bar_width_range):
                amps = data[(f-bar_width_range<data[:,0]) & (data[:,0]<f)]
                if not amps.size:
                    bars_samples = np.append(bars_samples, 0)
                else:
                    bars_samples = np.append(bars_samples, amps.max())

            for n, amp in enumerate(bars_samples):
                if amp > self.max_sample:
                    amp = self.max_sample
                elif bars[n] > 0 and amp < bars[n]:
                    amp = bars[n] * (2/3)
                else:
                    amp *= self.amplify_factor

                bars[n] = amp if amp > 1 else 0

            ax.clear()
            ax.grid(False)
            
            thetas = np.arange(0, math.pi*2, (2*math.pi)/(len(bars)*2))
            rs = np.concatenate((bars, np.flip(bars)))
            if self.polar:
                thetas = np.append(thetas, 0)
                rs = np.append(rs, rs[0]) + self.max_sample/3
                ax.set_rmax(self.max_sample)
            
            ax.plot(thetas, rs, color=matplotlib_stroke, linewidth=5)
            ax.set_ylim(top=self.max_sample, bottom=0)
            ax.set_theta_zero_location('N')
            ax.fill_between(thetas, rs, color=matplotlib_fill)
            plt.axis('off')
            plt.grid(b=None)

            image_io = io.BytesIO()

            canvas = plt.get_current_fig_manager().canvas
            canvas.draw()
            image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
            image = image.convert('RGBA')

            white = (255, 255, 255, 255)
            transparent = (0, 0, 0, 0)
            data = np.array(image)
            data[np.isin(data, (self.stroke_colour, self.fill_colour), invert=True).all(axis=-1)] = transparent
            transparent_image = Image.fromarray(data, mode='RGBA')
            
            background = self.background_image.copy()
            zoom = (bass_amplitude / self.max_sample)*(self.background_zoom - 1)
            if current_background_zoom*(2/3) < zoom:
                current_background_zoom = zoom
            else:
                current_background_zoom *= 0.5
            final = self.zoom_background(background, current_background_zoom + 1)
            # particles_gif = next(self.particle_frames).resize((1920, 1080))
            # particles_gif.show()
            # final.paste(particles_gif, (0, 0), particles_gif)
            final.paste(transparent_image, (0, 0), transparent_image)

            cv2_image = np.array(final)
            cv2_image = cv2_image[:, :, ::-1].copy()

            video.write(cv2_image)

            self.progress.emit(timestamp)

        cv2.destroyAllWindows()
        video.release()
        subprocess.call(f'ffmpeg -i tmp.mp4 -i {self.audio_file} -codec copy -shortest -y {self.video_output}')
        os.remove('tmp.mp4')
