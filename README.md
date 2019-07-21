# Visualise

### The calculations

The audio visualiser was created using an FFT (fast fourier transform) algorithm to calculate the amplitudes and frequencies of the samples. Using numpy and pydub, the values were calculated using the following method:

```python
from pydub import AudioSegment
import numpy as np

# the song is set to 1 channel so that it doesn’t contain duplicate samples
song = AudioSegment.from_file("sample.mp3").set_channels(1)
samples = np.array(song.get_array_of_samples)
# the fft algorithm calculates the amps and frequencies
fourier = np.fft.fft(samples)
frequencies = np.fft.fftfreq(fourier.size, d=song.duration)
amps = 2/samples.size * np.abs(fourier)
```

To learn more about FFTs go [here](https://www.nti-audio.com/en/support/know-how/fast-fourier-transform-fft).

### The visuals

The audio visualiser is displayed using polar coordinate formulae, if you didn’t know, you can plot into a circle very easily using the equations

```
y = rsinθ
x = rcosθ
```

Where `r` is the distance from the origin, and θ is the angle away from the positive x axis in the counterclockwise direction (in radians). Having x and y values makes it much easier to plot with Qt’s QPolygonF class as it uses cartesian coordinates to represent each point.

So plotting the visualiser in this way was quite easy as it allows you to let r = amplitude and plot them all with even intervals of θ.
