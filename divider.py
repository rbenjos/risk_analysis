import numpy as np
import pandas as pd
import json
import os
import sys
import logging


def divider(directory, filename):
    """
    takes in a long list of primaries, and divides them into different files, each for a separate meter, so looking
    at them individually would be easier. not necessarily used in the total aggregation, but might be used for
    taking a closer look on them without loading millions of rows each time
    :param directory: the directory in which the primaries are found
    :param filename: the filename of the primaries csv file. (usualy primaries_simplified.csv)
    :return:
    """

    # to not overload the memory, we will do the dividing chunk by chunk
    chunks = pd.read_csv(f"{directory}\\{filename}", chunksize=10000)

    # create the stations directory if needed
    if not os.path.exists(f"{directory}\\stations"):
        os.mkdir(f"{directory}\\stations")

    # and divide it to different stations:
    for chunk in chunks:
        chunk['timeFrom'] = pd.DatetimeIndex(chunk['timeFrom'])
        station_ids = chunk['ownerId'].unique()
        stations_dfs = {station_id: chunk[chunk['ownerId'] == station_id] for station_id in station_ids}
        for station_id, df in stations_dfs.items():
            # notice we are using 'append' mode to not overwrite previous recording from stations if exist
            df.to_csv(f"{directory}\stations\\{station_id}.csv",
                      index=False, mode='a', header=False)

            logging.info(f"saving to station: {station_id}")


if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    logging.basicConfig(filename=f'{directory}\\logfile.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    divider(directory, filename)
