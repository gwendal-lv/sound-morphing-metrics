
from pathlib import Path
from typing import Union, Sequence

import pandas as pd
import numpy as np

from . import timbral_models
from . import timbrefeatures


# TODO other args: matlab path (otherwise matlab is deactivated), verbose, ...
def compute_metrics(
        morphing_directories: Sequence[Union[str, Path]],

        skip_timbre_toolbox=False,
        sort_function=sorted,
):
    # TODO doc
    #    Each morphing directory must contain a sequence
    # Retrieve and sort all audio files that should be analyzed
    audio_files_types = ('.wav', )  # TODO improve, soundfile does not support .mp3
    morphing_directories = [Path(d) for d in morphing_directories]
    audio_files_path = [list() for _ in morphing_directories]
    for i, morphing_dir in enumerate(morphing_directories):
        audio_files = sort_function([f for f in morphing_dir.glob('*') if (f.suffix in audio_files_types)])
        assert len(audio_files) >= 3, \
            f"Morphing directory {morphing_dir} must contain more than 3 audio files ({len(audio_files)} files found)"
        audio_files_path[i] = audio_files

    # TODO compute AudioCommons Timbral Models features
    all_ac_features = list()
    for morphing_index, (morphing_dir, audio_files) in enumerate(zip(morphing_directories, audio_files_path)):
        all_ac_features.append(list())
        for audio_index, a in enumerate(audio_files):
            ac_features = timbral_models.Extractor.timbral_extractor(str(a), exclude_reverb=True)
            ac_features = {f'ac_{k}': v for k, v in ac_features.items()}
            all_ac_features[-1].append({
                'morphing_index': morphing_index,
                'morphing_name': morphing_dir.name,
                'morphing_dir': str(morphing_dir),
                'audio_index': audio_index,
                'audio_file': str(a),
                **ac_features
            })
    all_ac_features = [pd.DataFrame(features) for features in all_ac_features]

    if not skip_timbre_toolbox:
        raise NotImplementedError("Matlab TT call not implemented")

    # TODO Concatenate ACTM and TT features into wider dataframes,
    #   then concatenate all morphing sequences into a single long dataframe
    all_raw_features = all_ac_features  # TODO append TT features...
    all_raw_features = pd.concat(all_raw_features)

    # feature values post-processing (log scales, normalizations, ...)
    timbre_features = timbrefeatures.TimbreFeatures(all_raw_features)

    # TODO Compute morphing metrics for each morphing directory, then aggregate results into a dataframe
    all_morphing_metrics = list()
    morphing_description_cols = [c for c in all_raw_features.columns if c.startswith('morphing_')]
    for morphing_index, _ in enumerate(morphing_directories):
        morphing_features = timbre_features.postproc_df[timbre_features.postproc_df.morphing_index == morphing_index]
        morphing_metrics = {'nonsmoothness': dict(), 'nonlinearity': dict()}
        step_h = 1.0 / (len(morphing_features) - 1.0)
        for feature_name in timbre_features.feature_cols:
            feature_values = morphing_features[feature_name].values
            # Smoothness: https://proceedings.neurips.cc/paper/2019/file/7d12b66d3df6af8d429c1a357d8b9e1a-Paper.pdf
            # Second-order central difference using a conv kernel, then compute the RMS of the smaller array
            #   We'll name it "nonsmoothness" here
            smoothness = np.convolve(feature_values, [1.0, -2.0, 1.0], mode='valid') / (step_h ** 2)
            morphing_metrics['nonsmoothness'][feature_name] = np.sqrt( (smoothness ** 2).mean() )
            # non-linearity, quantified as the RMS of the error vs. the ideal linear curve
            target_linear_values = np.linspace(feature_values[0], feature_values[-1], num=feature_values.shape[0]).T
            morphing_metrics['nonlinearity'][feature_name] = np.sqrt( ((feature_values - target_linear_values) ** 2).mean() )
        for metric_name in ['nonsmoothness', 'nonlinearity']:
            all_morphing_metrics.append({
                **dict(morphing_features[morphing_description_cols].iloc[0]),
                'metric': metric_name,
                **morphing_metrics[metric_name]
            })
        a = 0
    all_morphing_metrics = pd.DataFrame(all_morphing_metrics)

    # TODO Don't return highly correlated features

    return all_morphing_metrics, timbre_features.postproc_df


