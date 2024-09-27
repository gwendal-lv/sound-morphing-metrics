import pathlib

if __name__ == "__main__":

    import socket
    print(f"Machine: '{socket.gethostname()}'")


    import src.soundmm

    morphing_directories = [
        'examples/data/good_morphing',
        'examples/data/subpar_morphing',
        'examples/data/random_sequence',
    ]

    morphing_metrics, timbre_features = src.soundmm.metrics.compute_metrics(
        morphing_directories,
        # timbre_toolbox_path='~/Documents/MATLAB/timbretoolbox',
        normalize=True,
        positive_metrics=False,
        verbose=True,
    )

    print(morphing_metrics.to_string())

