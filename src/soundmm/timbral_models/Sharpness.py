"""
Sharpness.py

Authors:
2018 Andy Pearce, Institute of Sound Recording, University of Surrey, UK
2023 Gwendal Le Vaillant, University of Mons, Belgium
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""

from __future__ import division
import numpy as np
import soundfile as sf
from . import timbral_util


def sharpness_Fastl(loudspec):
    """
      Calculates the sharpness based on FASTL (1991)
      Expression for weighting function obtained by fitting an
      equation to data given in 'Psychoacoustics: Facts and Models'
      using MATLAB basic fitting function
      Original Matlab code by Claire Churchill Sep 2004
      Transcoded by Andy Pearce 2018
    """
    n = len(loudspec)
    gz = np.ones(140)
    z = np.arange(141,n+1)
    gzz = 0.00012 * (z/10.0) ** 4 - 0.0056 * (z/10.0) ** 3 + 0.1 * (z/10.0) ** 2 -0.81 * (z/10.0) + 3.5
    gz = np.concatenate((gz, gzz))
    z = np.arange(0.1, n/10.0+0.1, 0.1)

    sharp = 0.11 * np.sum(loudspec * gz * z * 0.1) / np.sum(loudspec * 0.1)
    return sharp


def timbral_sharpness(audio_data, dev_output=False, clip_output=False):
    """
     This is an implementation of the matlab sharpness function found at:
     https://www.salford.ac.uk/research/sirc/research-groups/acoustics/psychoacoustics/sound-quality-making-products-sound-better/accordion/sound-quality-testing/matlab-codes

     This function calculates the apparent Sharpness of an audio file.
     This version of timbral_sharpness contains self loudness normalising methods and can accept arrays as an input
     instead of a string filename.

     Version 0.4

     Originally coded by Claire Churchill Sep 2004
     Transcoded by Andy Pearce 2018

     Required parameter
      :param  audio_data: TODO doc

     Optional parameters
      :param dev_output:              bool, when False return the warmth, when True return all extracted features
      :param phase_correction:        bool, if the inter-channel phase should be estimated when performing a mono sum.
                                      Defaults to False.
      :param clip_output:             bool, bool, force the output to be between 0 and 100.  Defaults to False.

      :return                         Apparent sharpness of the audio file.


     Copyright 2018 Andy Pearce, Institute of Sound Recording, University of Surrey, UK.

     Licensed under the Apache License, Version 2.0 (the "License");
     you may not use this file except in compliance with the License.
     You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

     Unless required by applicable law or agreed to in writing, software
     distributed under the License is distributed on an "AS IS" BASIS,
     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     See the License for the specific language governing permissions and
     limitations under the License.

    """
    '''
      Read input
    '''
    audio_samples, fs, windowed_audio = audio_data['audio_samples'], audio_data['fs'], audio_data['windowed_audio']

    windowed_sharpness = []
    windowed_rms = audio_data['windows_RMS']
    for i in range(windowed_audio.shape[0]):
        # calculate the specific loudness
        N_entire, N_single = audio_data['windows_specific_loudness'][i]

        # calculate the sharpness if section contains audio
        if N_entire > 0:
            sharpness = sharpness_Fastl(N_single)
        else:
            sharpness = 0

        windowed_sharpness.append(sharpness)

    # convert lists to numpy arrays for fancy indexing
    windowed_sharpness = np.array(windowed_sharpness)
    # calculate the sharpness as the rms-weighted average of sharpness
    rms_sharpness = np.average(windowed_sharpness, weights=(windowed_rms * windowed_rms))

    # take the logarithm to better much subjective ratings
    rms_sharpness = np.log10(rms_sharpness)

    if dev_output:
        return [rms_sharpness]
    else:

        all_metrics = np.ones(2)
        all_metrics[0] = rms_sharpness

        # coefficients from linear regression
        coefficients = [102.50508921364404, 34.432655185001735]

        # apply regression
        sharpness = np.sum(all_metrics * coefficients)

        if clip_output:
            sharpness = timbral_util.output_clip(sharpness)

        return sharpness
