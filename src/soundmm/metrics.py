
from pathlib import Path
from typing import Union, Sequence

import soundfile as sf

from . import timbral_models

def compute_metrics(
        morphing_directories: Sequence[Union[str, Path]],

        skip_timbre_toolbox=False,
        sort_function=sorted,
):
    # TODO doc
    # Retrieve and sort all audio files that should be analyzed
    audio_files_types = ('.wav', )  # TODO improve, soundfile does not support .mp3
    morphing_directories = [Path(d) for d in morphing_directories]
    audio_files_path = [list() for _ in morphing_directories]
    for i, morphing_dir in enumerate(morphing_directories):
        audio_files = sort_function([f for f in morphing_dir.glob('*') if (f.suffix in audio_files_types)])
        audio_files_path[i] = audio_files

    # TODO compute AudioCommons Timbral Models features
    #all_feature
    for morphing_dir, audio_files in zip(morphing_directories, audio_files_path):
        for a in audio_files:
            # TODO exclude reverb parameter ????
            ac_features = timbral_models.Extractor.timbral_extractor(str(a), exclude_reverb=True)
            raise NotImplementedError()


    if not skip_timbre_toolbox:
        raise NotImplementedError("Matlab TT call not implemented")

