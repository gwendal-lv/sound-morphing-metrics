# soundmm: Sound Morphing Metrics

In order to compute the metrics of a given morphing, the ```soundmm``` package can compute 
audio features for each individual morphed audio sample.
Then, the *smoothness* and *linearity* morphing metrics can be extracted for each audio feature.

Detailed examples and usage instructions are given in the 
[examples/soundmm_demo.ipynb](examples/soundmm_demo.ipynb) notebook from this repository.

# Dependencies

This project uses the [timbral_models](https://github.com/AudioCommons/timbral_models) package whose dependencies are the following:

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

# Citing

If you use our work, please cite the following article: 

```
@ARTICLE{LeVaillant_2024,
  author={Le Vaillant, Gwendal and Dutoit, Thierry},
  journal={IEEE/ACM Transactions on Audio, Speech, and Language Processing}, 
  title={Latent Space Interpolation of Synthesizer Parameters Using Timbre-Regularized Auto-Encoders}, 
  year={2024},
  volume={32},
  pages={3379-3392},
  doi={10.1109/TASLP.2024.3426987}}
```
