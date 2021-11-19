# %%

import numpy as np
import pandas as pd
import logging
from scipy.stats import norm, gaussian_kde
from utils import logfile
import os
import sys

print("done importing")


def aggregate(directory, filename):
    """
    a simpler aggreagor, only aggregating the total pivot table, and not the individual ones.
    also doesn't asses risk
    :param directory: the directory in which the primaries are found
    :param filename: the filename of the primaries csv file. (usualy primaries_simplified.csv)
    :return:
    """
    df = pd.read_csv(f'{directory}\\{filename}')
    df['ownerId'] = df['ownerId'].astype(str)
    ownerIds = df['ownerId'].unique()
    pt = pd.pivot_table(data=df, values='prognoses', index='timeFrom', columns='modelId', aggfunc=np.sum)
    pt.to_csv(f'{directory}\\total_aggregate.csv',header=True)

    # lets log the maximum value for that aggregate so we can save it for later
    logging.info(f'maximum value is :{pt.max()}')
    

if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    logging.basicConfig(filename=f'{directory}\\logfile.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    aggregate(directory, filename)
