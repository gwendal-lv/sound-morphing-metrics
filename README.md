# soundmm: Sound Morphing Metrics

In order to compute the metrics of a given morphing, the ```soundmm``` package can compute 
audio features for each individual morphed audio sample.
Then, the *smoothness* and *non-linearity* morphing metrics can be extracted for each audio feature.

Detailed examples and usage instructions are given in the 
[examples/soundmm_demo.ipynb](examples/soundmm_demo.ipynb) notebook from this repository.

This work has been introduced in our IEEE ICASSP 2023 paper 
titled [Synthesizer Preset Interpolation Using Transformer Auto-Encoders](https://ieeexplore.ieee.org/document/10096397).

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

The easiest way to use this package is to integrate the [src/soundmm](src/soundmm) directory into your
Python project.

Please refer to the [examples/soundmm_demo.ipynb](examples/soundmm_demo.ipynb) notebook to get more detailed instructions.

# Citing

If you use our work, please cite the ICASSP 2023 paper:

```
@INPROCEEDINGS{10096397,
  author={Le Vaillant, Gwendal and Dutoit, Thierry},
  booktitle={ICASSP 2023 - 2023 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)}, 
  title={Synthesizer Preset Interpolation Using Transformer Auto-Encoders}, 
  year={2023},
  pages={1-5},
  doi={10.1109/ICASSP49357.2023.10096397}
}
```
