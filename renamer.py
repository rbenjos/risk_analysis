import numpy as np
import pandas as pd
import os
import sys

def rename(directory,meters_file):
    """

    :param directory:
    :param meters_file:
    :return:
    """
    meters = pd.read_csv(f'{directory}\\..\\{meters_file}')

    def meter_to_name(meterId):
        """
        converts from meter id to the station name using
        the OPC-meters.csv file supplied
        :param meterId: the meter's id
        :return: the station's name
        """
        stations_name = meters.loc[meters['meterId'] == meterId]['name']
        if len(stations_name) == 0:
            return meterId
        return stations_name.values[0]

    for file in os.listdir(f"{directory}\\stations_agg"):
        name = (file.split('.')[:-1])
        new_name = meter_to_name(name)
        if file in os.listdir(f"{directory}\\stations_agg"):
            os.rename(f'{directory}\\stations_agg\\{file}', f'{directory}\\stations_agg\\{new_name}.csv')

if __name__ == "__main__":
    directory, meters_file = sys.argv[1], int(sys.argv[2])
    rename(directory, meters_file)

