import warnings
from pathlib import Path
from typing import Union, Sequence, Optional
import tempfile

import pandas as pd
import numpy as np

from . import timbral_models
from . import timbrefeatures
from .timbretoolbox import TimbreToolboxProcess, TimbreToolboxResults


def compute_metrics(
        morphing_directories: Sequence[Union[str, Path]],
        timbre_toolbox_path: Optional[Union[str, Path]] = None,
        positive_metrics=False,
        normalize=False,
        verbose=False,
        sort_function=sorted,
):
    """
    Computes morphing metrics (non-smoothness and non-linearity) for sequences of sounds stored in individual
    directories. Batch processing is faster, thus several directories (morphings) should be provided to this function.

    :param morphing_directories: Each morphing directory must contain a sequence of morphed audio files.
    :param timbre_toolbox_path: The path to your TimbreToolbox installation -
        see https://github.com/VincentPerreault0/timbretoolbox for instructions. If not provided,
        TimbreToolbox features and associated morphing metrics will not be computed.
    :param positive_metrics: If False (default), returns negative values with increasing values (towards 0.0)
        indicating a better morphing. If True, returns positive values with decreasing values (towards 0.0) indicating
        a better morphing.
    :param normalize: if True, metric values (for a given audio feature) will be normalized such that
        their mean is 1.0.
    :param verbose: bool
    :param sort_function: An optional custom function to sort each morphed sequence of files it its own  directory.
    :returns: morphing_metrics, timbre_features (Pandas DataFrames)
    """
    metrics_names = ('nonsmoothness', 'nonlinearity')
    # Retrieve and sort all audio files that should be analyzed
    audio_files_types = ('.wav', )  # TODO improve, soundfile does not support .mp3
    morphing_directories = [Path(d) for d in morphing_directories]
    audio_files_path = [list() for _ in morphing_directories]
    for i, morphing_dir in enumerate(morphing_directories):
        audio_files = sort_function([f for f in morphing_dir.glob('*') if (f.suffix in audio_files_types)])
        assert len(audio_files) >= 3, \
            f"Morphing directory {morphing_dir} must contain more than 3 audio files ({len(audio_files)} files found)"
        audio_files_path[i] = audio_files

    # compute AudioCommons Timbral Models features
    if verbose:
        print("Computing AudioCommons Timbral Models features...")
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

    if timbre_toolbox_path is not None:
        # Prepare directories for results storage (matlab will store results as .csv in those dirs)
        tt_results = TimbreToolboxResults(morphing_directories, audio_files_path)
        tt_results.clean_stats_files()
        # build a file that contains all directories to be analyzed in a single Matlab call
        with tempfile.NamedTemporaryFile('w') as matlab_input_file:
            # Absolute paths required (the matlab script will cd)
            for d in morphing_directories:
                matlab_input_file.write(str(d.resolve()) + "\n")
            matlab_input_file.flush()
            # TODO run TT
            # TODO pre-cleanup
            tt_process = TimbreToolboxProcess(
                Path(timbre_toolbox_path), Path(matlab_input_file.name), verbose=verbose, process_index=0)
            tt_process.run()
        # Retrieve results and clean temp .csv files
        all_tt_features = tt_results.read()
        tt_results.clean_stats_files()
        # And transform features into proper dataframes (similar to AC dfs)
        for morphing_index, _ in enumerate(morphing_directories):
            for j in range(len(all_tt_features[morphing_index])):
                all_tt_features[morphing_index][j] = \
                    {f'tt_{k}': v for k, v in all_tt_features[morphing_index][j].items()}
            all_tt_features[morphing_index] = pd.DataFrame(all_tt_features[morphing_index])
    else:
        all_tt_features = None
        if verbose:
            print("TimbreToolbox path was not provided, so the corresponding audio features won't be computed")

    # Concatenate all morphing sequences into a long dataframes
    #     concatenate ACTM and TT features into wider dataframes,
    all_ac_features = pd.concat(all_ac_features, axis=0)
    if all_tt_features is not None:
        all_tt_features = pd.concat(all_tt_features, axis=0)
        all_raw_features = pd.concat((all_ac_features, all_tt_features), axis=1)
    else:
        all_raw_features = all_ac_features

    # feature values post-processing (log scales, normalizations, ...)
    timbre_features = timbrefeatures.TimbreFeatures(all_raw_features)

    # Compute morphing metrics for each morphing directory, then aggregate results into a dataframe
    all_morphing_metrics = list()
    morphing_description_cols = [c for c in all_raw_features.columns if c.startswith('morphing_')]
    for morphing_index, _ in enumerate(morphing_directories):
        morphing_features = timbre_features.postproc_df[timbre_features.postproc_df.morphing_index == morphing_index]
        morphing_metrics = {m: dict() for m in metrics_names}
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
        for m in metrics_names:
            all_morphing_metrics.append({
                **dict(morphing_features[morphing_description_cols].iloc[0]),
                'metric': m,
                **morphing_metrics[m]
            })
    all_morphing_metrics = pd.DataFrame(all_morphing_metrics)

    # Normalization, if required
    if normalize:
        for m in metrics_names:
            means = all_morphing_metrics[all_morphing_metrics.metric == m][timbre_features.feature_cols].mean()
            all_morphing_metrics.loc[all_morphing_metrics.metric == m, timbre_features.feature_cols] /= means
    if not positive_metrics:  # Return smoothness/linearity instead of nonsmoothness/nonlinearity
        all_morphing_metrics[timbre_features.feature_cols] *= -1.0
        all_morphing_metrics['metric'] = all_morphing_metrics['metric'].apply(lambda x: x.replace('non', ''))

    return all_morphing_metrics, timbre_features.postproc_df


