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

    pts_ind = {}
    import os
    if not os.path.exists(f"{directory}\\stations_agg"):
        os.mkdir(f"{directory}\\stations_agg")
    for counter, owner in enumerate(ownerIds):
        df_partial = df[df['ownerId'] == owner]
        pts_ind[owner] = pd.pivot_table(data=df_partial, values='prognoses', index='timeFrom', columns='modelId',
                                        aggfunc=np.sum)
        pts_ind[owner].to_csv(f"{directory}\stations_agg\\{owner}.csv")
        log(f'done summarizing station {owner}. {counter}/{len(ownerIds)}')

    pt = pd.pivot_table(data=df, values='prognoses', index='timeFrom', columns='modelId', aggfunc=np.sum)
    agg_without = {}
    if not os.path.exists(f"{directory}\\stations_agg_without"):
        os.mkdir(f"{directory}\\stations_agg_without")
    for counter, owner in enumerate(ownerIds):
        agg_without[owner] = pt.subtract(pts_ind[owner], fill_value=0)
        print(f'done subtracting station {owner}. {counter}/{len(ownerIds)}')
        agg_without[owner].to_csv(f"{directory}\\stations_agg_without\\{owner}.csv", header=True)

    print('done summarizing and subtracting')

    max_val = pt.max().max() * 1.2
    min_val = pt.min().min() / 0.8

    def integrate_cdf(row, minv=min_val, maxv=max_val, res=100):
        val = row.dropna().values
        bw = 0.04
        kernel = gaussian_kde(val, bw_method=bw)
        space = np.linspace(minv, maxv, res)
        cumulative = [kernel.integrate_box_1d(0, value) for value in space]
        return (1 - pd.Series(cumulative))

    def make_discrete_cdf(row, minv=min_val, maxv=max_val, res=100):
        models = row.dropna().values
        space = np.linspace(minv, maxv, res)
        cumulative = pd.Series([(value < models).sum() for value in space])
        return cumulative / cumulative.max()

    all_risk = pt.apply(integrate_cdf, axis=1)
    all_risk.columns = np.linspace(min_val, max_val, 100)

    print("done assesing total risk")

    max_risk_diff = {}
    for counter, owner in enumerate(ownerIds):
        risk_without = agg_without[owner].apply(integrate_cdf, axis=1)
        risk_without.columns = np.linspace(min_val, max_val, 100)
        risk_diff = all_risk.subtract(risk_without, fill_value=0)
        max_risk_diff[owner] = risk_diff.max(axis=0)
        message = f'done assesing risk of station {owner}. {counter}/{len(ownerIds)}'
        log(message)
        print(message)

    max_risk_station = pd.DataFrame(max_risk_diff)
    max_risk_station.to_csv(f'{directory}\\added_risk_by_station_smooth.csv', header=True)
    print('wrote smooth version')


if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    log = logfile(directory)
    aggregate(directory, filename, log)
