# %%

import numpy as np
import pandas as pd

from scipy.stats import norm, gaussian_kde
from utils import logfile
import os
import sys

print("done importing")


def aggregate(directory, filename, log):
    df = pd.read_csv(f'{directory}\\{filename}')
    df['ownerId'] = df['ownerId'].astype(str)
    ownerIds = df['ownerId'].unique()
    pt = pd.pivot_table(data=df, values='prognoses', index='timeFrom', columns='modelId', aggfunc=np.sum)
    pt.to_csv(f'{directory}\\total_aggregate.csv',header=True)
    print(pt.max())
    

if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    log = logfile(directory)
    aggregate(directory, filename, log)
