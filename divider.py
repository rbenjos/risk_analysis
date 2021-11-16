
import numpy as np
import pandas as pd
import json
import os
from utils import logfile
import sys

def divider(directory, filename,log):
    chunks = pd.read_csv(f"{directory}\\{filename}", chunksize=10000)
    if not os.path.exists(f"{directory}\\stations"):
        os.mkdir(f"{directory}\\stations")
    # lets divide it to different stations:
    for chunk in chunks:
        chunk['timeFrom'] = pd.DatetimeIndex(chunk['timeFrom'])
        station_ids = chunk['ownerId'].unique()
        stations_dfs = {station_id: chunk[chunk['ownerId'] == station_id] for station_id in station_ids}
        for station_id, df in stations_dfs.items():
            df.to_csv(f"{directory}\stations\\{station_id}.csv",
                      index=False, mode='a', header=False)

            log(f"saving to station: {station_id}")



if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    log = logfile(directory)
    divider(directory, filename, log)

