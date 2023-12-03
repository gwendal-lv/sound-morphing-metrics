# soundmm: Sound Morphing Metrics

In order to compute the metrics of a given morphing, the ```soundmm``` package can compute 
audio features for each individual morphed audio sample.
Then, the *smoothness* and *non-linearity* morphing metrics can be extracted for each audio feature.

Detailed examples and usage instructions are given in the 
[examples/soundmm_demo.ipynb](examples/soundmm_demo.ipynb) notebook from this repository.

# Dependencies

This project is mostly based on a Python package whose dependencies are the following:

```
pip3 install numpy pandas scipy soundfile librosa pyloudnorm
```

The Python package in this repository allows to compute audio features (and morphing metrics) based on 
[AudioCommons Timbral Models](https://github.com/AudioCommons/timbral_models).

An extended set of audio features can be computed using [Timbre Toolbox](https://github.com/VincentPerreault0/timbretoolbox),
but this requires a local Matlab install and the toolbox to be compiled. 
Please check instructions on their Github repository.

# Usage

The easiest way to use this package is to copy the [src/soundmm](src/soundmm) directory into your
Python project.

Please refer to the [examples/soundmm_demo.ipynb](examples/soundmm_demo.ipynb) notebook to get more detailed instructions.


