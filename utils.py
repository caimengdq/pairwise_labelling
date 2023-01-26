from ast import literal_eval
from asap import *
from os.path import join
import os
import pandas as pd
import numpy as np
import choix
from random import sample
from tkinter_interface import *


def prepare_photos(path):
    """
    This function will gather all the photos appeared in the paired photo folder and saves a csv with photo index to
    be used for ASAP later
    :param path: path of directory of paired photos where filename is the combination of two photo ids
    :param view: example: 'ocf'
    :return: the list of the photo ids in this path
    """
    val_for = ['jpg', 'jpeg', 'png']
    img_list = os.listdir(path)
    img_list = [i for i in img_list if i.split('.')[-1] in val_for]

    # put all possible pairs in two separate lists
    photo_id_1 = []
    photo_id_2 = []
    for photo in img_list:
        strings = photo.split("_")
        photo_1 = strings[0] + '_' + strings[1] + '_' + strings[2]
        photo_2 = strings[3] + '_' + strings[4] + '_' + strings[5][:-4]
        photo_id_1.append(photo_1)
        photo_id_2.append(photo_2)

    # create dictionary with index for all photos to be used for matirx
    photos = list(set(photo_id_1 + photo_id_2))
    print(f"this folder has {len(photos)} photos")
    return photos


def get_dict_photos(photos, filename_to_save=None):
    dict_photos = {k: v for k, v in enumerate(photos)}
    # save photo_id and index in a csv
    df_dict = pd.DataFrame.from_dict(dict_photos, orient='index', columns=['photo_id'])
    df_dict.reset_index(inplace=True)
    df_dict.to_csv(f"photo_index_{filename_to_save}.csv", index=False)
    return dict_photos


def find_pair_in_path(path, pair, name_photo_1, name_photo_2, labelled_pairs):
    if os.path.isfile(join(path, f"{name_photo_1}_{name_photo_2}.png")):
        filename = f"{name_photo_1}_{name_photo_2}.png"
        labelled_pairs.append(filename)
    elif os.path.isfile(join(path, f"{name_photo_2}_{name_photo_1}.png")):
        filename = f"{name_photo_2}_{name_photo_1}.png"
        pair = (pair[1], pair[0])
        labelled_pairs.append(filename)
    return pair


def update_matrix(label, M, index_photo_1, index_photo_2):
    # Update the matrix before running ASAP
    if label == 0:
        M[index_photo_1][index_photo_2] += 1
    elif label == 1:
        M[index_photo_2][index_photo_1] += 1
    return M


def update_pairs_to_rank(label, pairs_to_rank, pair):
    if label == 0:
        pairs_to_rank.append((pair[0], pair[1]))
    elif label == 1:
        pairs_to_rank.append((pair[1], pair[0]))
    return pairs_to_rank


def update_labels(dict_photos, label, labels_list, pair):
    if label == 0:
        labels_list.append(dict_photos[pair[0]])
    elif label == 1:
        labels_list.append(dict_photos[pair[1]])
    return labels_list


def update_photo_index(label, photo_index, pair):
    if label == 0:
        photo_index.append(pair[0])
    elif label == 1:
        photo_index.append(pair[1])
    return


def random_sampling(path, M, photos, filename_to_save=None, sample_n=None):
    """
    Adding randomly selected pairs to label first and then update the matrix for the input of ASAP
    :param path: paired images' directory path
    :param M: matrix to pass to ASAP for calculation
    :param photos: use prepare_photos(path) to get all the existing photos in all pairs
    :param filename_to_save: name to save in the csv file with all the labels and the pair index in tuples with the winning one comes first
    :param sample_n:
    :return:
    """
    # sampling some pairs to label first
    index_list = [i for i in range(len(photos))]
    all_pairs = [(index_list[i], index_list[j]) for i in range(len(index_list)) for j in range(i + 1, len(index_list))]
    dict_photos = get_dict_photos(photos)
    n_labelled = 0
    labelled_pairs = []
    labels = []
    index = []
    photo_index = []
    pairs_to_rank = []

    # randomly select n of the possible pairs(sample_n) to label first
    pairs_to_compare = sample(all_pairs, sample_n)
    print(f"Random pairs to label first: {pairs_to_compare}")
    for pair in pairs_to_compare:
        # get photo id
        index_photo_1, index_photo_2 = pair
        name_photo_1, name_photo_2 = dict_photos[index_photo_1], dict_photos[index_photo_2]
        # Find filename
        if os.path.isfile(join(path, f"{name_photo_1}_{name_photo_2}.png")):
            filename = f"{name_photo_1}_{name_photo_2}.png"
        elif os.path.isfile(join(path, f"{name_photo_2}_{name_photo_1}.png")):
            filename = f"{name_photo_2}_{name_photo_1}.png"
            pair = (pair[1], pair[0])
        else:
            continue
        labelled_pairs.append(filename)

        # load image to label
        img_path = join(path, filename)
        open_label_window(img_path, index_list=index)
        # label(0 or 1) is the last element of the list
        label = index[-1]
        # print(f"photo {label} is chosen")
        # update the number of labelled images
        n_labelled = n_labelled + 1
        print(f"labelled {n_labelled} photos")
        # update labels, matrix, pairs to rank(the winning one comes first in tuple)
        update_labels(dict_photos, label, labels, pair)
        update_matrix(label, M, index_photo_1, index_photo_2)
        update_pairs_to_rank(label, pairs_to_rank, pair)
        update_photo_index(label, photo_index, pair)
    # save csv
    data = {'Image': labelled_pairs, 'Label': labels, 'Photo_index': photo_index, 'Pairs_to_rank': pairs_to_rank}
    df = pd.DataFrame(data)
    df.to_csv(f"random_labels_{filename_to_save}.csv", index=False)
    print('\nrandom selected pairs labelled csv saved!')
    # print(M.sum())
    return M, n_labelled, pairs_to_rank, labelled_pairs, labels, photo_index, index


def check_ranking(n_diffs, photos, pairs_to_rank, n_labelled):
    last_ranking = np.argsort(choix.ilsr_pairwise(len(photos), pairs_to_rank[:n_labelled - 1], alpha=0.01))
    ranking = np.argsort(choix.ilsr_pairwise(len(photos), pairs_to_rank, alpha=0.01))
    # count number of differences
    n_diff = np.sum([i != j for i, j in zip(last_ranking, ranking)])
    print(f"after labelling {n_labelled} pairs the ranking diff is :{n_diff}")
    n_diffs.append(n_diff)
    print(f"ranking difference of last five labels : {n_diffs[-5:]}")
    print(f"current ranking is : {ranking}")

    # if after labelling 3 pairs in a row no more change in ranking
    if n_diffs[-3:] == [0, 0, 0]:
        print(f"whole list of ranking differences after adding each label: {n_diffs}")
        print("Stop labelling")
        print(f"Ranking is : {ranking}")
    return ranking


def create_labels(path, label_n, sample_n, random=True, filename_to_save=None, add_label=False, label_file_path=None,
                  matrix_path=None):
    """
    Args: path of view directory, number of labelling I want to do
    """
    photos = prepare_photos(path)
    dict_photos = get_dict_photos(photos)
    # initialize empty matrix
    M = np.zeros((len(photos), len(photos)), dtype=int)
    N = M.shape[0]

    # Create an object of class passing the number of conditions
    asap = ASAP(N, approx=True)
    if random is True:
        M, n_labelled, pairs_to_rank, labelled_pairs, labels, photo_index, index = random_sampling(path, M, photos,
                                                                                                   sample_n=sample_n,
                                                                                                   filename_to_save=filename_to_save)
    elif add_label is True:
        M = np.load(matrix_path)
        df_label = pd.read_csv(label_file_path)
        df_label['Pairs_to_rank'] = df_label.Pairs_to_rank.apply(lambda x: literal_eval(str(x)))
        df_label['Photo_index'] = df_label.Photo_index.apply(lambda x: literal_eval(str(x)))
        n_labelled = df_label.shape[0]
        pairs_to_rank = list(df_label['Pairs_to_rank'])
        labelled_pairs = list(df_label['Image'])
        labels = list(df_label['Label'])
        photo_index = list(df_label['Photo_index'])
        index = []

    else:
        n_labelled = 0
        labelled_pairs = []
        labels = []
        index = []
        photo_index = []
        pairs_to_rank = []
    # prepare n_diffs list for ranking later
    n_diffs = []

    while n_labelled < label_n:
        # Run active sampling algorithm on the matrix of comparisons
        pairs_to_compare_asap = asap.run_asap(M, mst_mode=True)
        # labeling sampled number of photos each time after running ASAP
        for pair in pairs_to_compare_asap[:sample_n]:
            # get photo id
            index_photo_1, index_photo_2 = pair
            name_photo_1, name_photo_2 = dict_photos[index_photo_1], dict_photos[index_photo_2]
            # Find filename
            if os.path.isfile(join(path, f"{name_photo_1}_{name_photo_2}.png")):
                filename = f"{name_photo_1}_{name_photo_2}.png"
            elif os.path.isfile(join(path, f"{name_photo_2}_{name_photo_1}.png")):
                filename = f"{name_photo_2}_{name_photo_1}.png"
                pair = (pair[1], pair[0])
            else:
                continue
            labelled_pairs.append(filename)

            # load image to label
            img_path = join(path, filename)
            open_label_window(img_path, index_list=index)
            # label(0 or 1) is the last element of the list
            label = index[-1]
            # print(f"photo {label} is chosen")
            # update the number of labelled images
            n_labelled = n_labelled + 1
            print(f"labelled {n_labelled} photos")
            # update labels, matrix, pairs to rank(the winning one comes first in tuple)
            update_labels(dict_photos, label, labels, pair)
            update_matrix(label, M, index_photo_1, index_photo_2)
            update_pairs_to_rank(label, pairs_to_rank, pair)
            update_photo_index(label, photo_index, pair)
            print(f"number of pairs compared {len(pairs_to_rank)}")
            data = {'Image': labelled_pairs, 'Label': labels, 'Photo_index': photo_index,
                    'Pairs_to_rank': pairs_to_rank}
            df = pd.DataFrame(data)
            df.to_csv(f"labels_{filename_to_save}.csv", index=False)
            print('\nupdated version of labels.csv saved!')
            # check ranking after each new label
            check_ranking(n_diffs, photos, pairs_to_rank, n_labelled)

            # save data after each label
            # Binary data
            np.save(f"matrix_{filename_to_save}.npy", M)
            # Human readable data
            np.savetxt(f"matrix_{filename_to_save}.txt", M)

    ranking = check_ranking(n_diffs, photos, pairs_to_rank, n_labelled)
    return ranking


