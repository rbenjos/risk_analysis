# %%

import numpy as np
import pandas as pd
import json
import os
from utils import logfile
import sys


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
    rba_list = json.loads(json_string)
    rba_dic = json.loads(rba_list['rba'][0])
    return rba_dic['expected']


def extract_prognosis_value(json_string):
    rbe_list = json.loads(json_string)
    rbe_dic = json.loads(rbe_list['basic'][0])
    return rbe_dic['prognosisValue']


def simplify(directory, filename, log):
    chunks = pd.read_csv(f"{directory}\\{filename}", chunksize=10000)

    if not os.path.exists(directory):
        os.mkdir(directory)

    i = 0
    header = True
    for chunk in chunks:
        simplified_chunk = chunk[['modelId', 'ownerId', 'timeFrom', 'prognoses']]
        simp_prog = simplified_chunk['prognoses'].apply(simplify_prognoses)
        simplified_chunk.loc['prognoses'] = simp_prog

        simplified_chunk.to_csv(f"{directory}\primary_simplified.csv",
                                index=False, mode='a', header=header)
        log(f"saved chunk: {i}")
        i += 1
        header = False


if __name__ == "__main__":
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    log = logfile(directory)
    simplify(directory, filename, log)
