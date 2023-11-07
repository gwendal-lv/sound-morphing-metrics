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
    #project_base_path = pathlib.Path(__file__).parent.parent
    #morphing_directories = [project_base_path.joinpath(d) for d in morphing_directories]

    src.soundmm.metrics.compute_metrics(morphing_directories)

