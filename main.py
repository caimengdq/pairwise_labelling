from asap import *
from utils import create_labels

if __name__ == "__main__":
    # path to the folder of paired images
    pairs_path = ""
    max_labels = 10
    random_phase = False
    num_labels = 5
    filename = ""
    label_after_interruption = False
    label_file_path = ""
    matrix_path = ""

    # Label
    create_labels(path=pairs_path,
                  label_n=max_labels, sample_n=num_labels, random=random_phase, filename_to_save=filename,
                  add_label=label_after_interruption, label_file_path=label_file_path, matrix_path=matrix_path
                  )
