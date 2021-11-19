# %%

import numpy as np
import pandas as pd
import json
import os
import sys
import logging

def simplify_prognoses(json_string):
    """

    :param json_string: the string inside the "prognoses" column, representing
    some data structure out of which we want to extract the prediction alone
    without the additional info

    :return: the forementioned prediction
    """
    dic = json.loads(json_string)
    if 'rba' in dic:
        return extract_expected(json_string)
    elif 'basic' in dic:
        return extract_prognosis_value(json_string)
    else:
        return


def extract_expected(json_string):
    """
    extracting the prognosis from rows which contains the desired value under the title of 'expected'
    :param json_string: a jason string containing the data for this prediction
    :return: the expected prediction of this row
    """
    rba_list = json.loads(json_string)
    rba_dic = json.loads(rba_list['rba'][0])
    return rba_dic['expected']


def extract_prognosis_value(json_string):
    """
    extracting the prognosis from rows which contains the desired value under the title of 'PrognosisValue'
    :param json_string: a jason string containing the data for this prediction
    :return: the prognosis given in this row
    """
    rbe_list = json.loads(json_string)
    rbe_dic = json.loads(rbe_list['basic'][0])
    return rbe_dic['prognosisValue']


def simplify(directory, filename):
    """
    the main function of this file. given a large csv file of prognoses, it keeps the relevant columns,
    and extract the prognosis value given at each row, reudcing the csv file size by about 80 precent
    :param directory: the directory in which the primary csv file is found
    :param filename: the filename of the large primary csv file
    :return:
    """

    # to not overload the memory, we will process this csv file in chunks.

    chunks = pd.read_csv(f"{directory}\\{filename}", chunksize=10000)

    if not os.path.exists(directory):
        os.mkdir(directory)

    i = 0
    header = True
    for chunk in chunks:
        # keeping the relevant columns
        simplified_chunk = chunk[['modelId', 'ownerId', 'timeFrom', 'prognoses']]
        simp_prog = simplified_chunk['prognoses'].apply(simplify_prognoses)
        simplified_chunk['prognoses'] = simp_prog

        # appending it to the simplified csv file
        simplified_chunk.to_csv(f"{directory}\primary_simplified.csv",
                                index=False, mode='a', header=header)
        logging.info(f"saved chunk: {i}")
        i += 1
        # no need to save the header each time
        header = False


if __name__ == "__main__":
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    logging.basicConfig(filename=f'{directory}\\logfile.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    simplify(directory, filename)
