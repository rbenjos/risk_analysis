


import numpy as np
import pandas as pd
import os
import sys

print('done importing')




def rater(directory, rate):
    # estimating the most dangerous non must stations based on the added risk

    added_risk = pd.read_csv(f'{directory}\\added_risk_by_station_smooth.csv')
    added_risk.index = added_risk['Unnamed: 0']
    added_risk = added_risk.drop(columns='Unnamed: 0')

    # %%

    # lets read all the meters so we can map from meter number to the name of the station

    meters = pd.read_csv(f'{directory}\\..\\OPC-Meters.csv')

    def meter_to_name(meterId):
        name = meters.loc[meters['meterId'] == meterId]['name']
        if len(name) == 0:
            return meterId
        return name.values[0]

    # %%

    # and create the reverse mapper needed for renaming the columns
    new_columns = {column: meter_to_name(column) for column in added_risk.columns}

    # and rename them
    added_risk = added_risk.rename(columns=new_columns)

    # %%

    # reading the must stations (actualy customers)

    must_customers = pd.read_csv(f'{directory}\\..\\must_meters.csv')
    must_customers_vals = must_customers['Must Customers'].values

    # %%

    # and deriving the actual stations we need to keep (one customer -> many stations/meters)
    must_station = [station for station in added_risk.columns for must in must_customers_vals if must in station]
    pd.Series(must_station).to_csv(f'{directory}\\must_stations.csv')

    # finally lets drop them as they are not important in the risk analysis, they will stay anyway
    added_risk_non_must = added_risk.drop(columns=must_station)
    added_risk_non_must.to_csv(f'{directory}\\added_risk_non_must.csv')

    # %%

    # argsort gives us the argument, which we want to convert to the meter name
    mapper = {idx: column for idx, column in enumerate(added_risk_non_must.columns)}

    def f(idx):
        return mapper[idx]

    # sorting
    added_risk_sorted_idx = added_risk_non_must.values.argsort(axis=1)
    # mapping argument index to name and arrange in descending order
    stations_by_risk = pd.DataFrame(added_risk_sorted_idx).applymap(f).loc[::, ::-1]
    # re indexing
    stations_by_risk.index = added_risk_non_must.index
    stations_by_risk.to_csv(f'{directory}\\stations_by_risk.csv')

    # %%

    # finally lets save the meters in the order of risk so we can iterate over them and add one by one
    max_risk_stations = stations_by_risk.iloc[-1]
    max_risk_stations.to_csv(f'{directory}\\max_risk_stations.csv', index=False)

    # %%

    # now we need to rename all the aggregates files so we can iterate over them
    # %%

    # next thing we need to add these one by one until we reach a certain capacity
    # first lets add all the must statiosn

    must_pt = None
    maxes = {}

    # %%

    for idx, station in enumerate(must_station):
        if must_pt is None:
            print('first time')
            must_pt = pd.read_csv(f'{directory}\\stations_agg\\{station}.csv', index_col='timeFrom').fillna(0)
        else:
            station_pt = pd.read_csv(f'{directory}\\stations_agg\\{station}.csv', index_col='timeFrom').fillna(0)
            must_pt = must_pt.add(station_pt, fill_value=0)
        print(f'done adding station {station}, {idx}/{len(must_station)}')

    # %%

    # adjusting so it would be kWh
    must_pt *= 2

    # %%

    must_pt.max().max()

    # %%

    least_risky = max_risk_stations[::-1]
    all_pt = must_pt
    non_must_pt = None
    for idx, station in enumerate(least_risky):
        station_pt = pd.read_csv(f'{directory}\stations_agg\\{station}.csv', index_col='timeFrom').fillna(0)
        # again adjusting the consumption rate
        station_pt *= 2
        all_pt = all_pt.add(station_pt, fill_value=0)
        if all_pt.max().max() > rate * 10000:
            all_pt = all_pt.subtract(station_pt, fill_value=0)
            break
        print(f'done adding station {station}, {idx}/{len(least_risky)}')

    # %%

    print(all_pt.max().max())
    least_risky[:idx].to_csv(f'{directory}\\stations_to_{rate}.csv')

    # %%

    all_pt.to_csv(f'{directory}\\aggregate_to_{rate}.csv', header=True)


if __name__ == "__main__":
    directory,rate = sys.argv[1],int(sys.argv[2])
    rater(directory, rate)
