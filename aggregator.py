# %%

import numpy as np
import pandas as pd
import logging
from scipy.stats import norm, gaussian_kde
import os
import sys


def aggregate(directory, filename):
    """
    this function does 3 things:
    it aggregates pivot tables of all the meters
    it aggregates pivot tables of the total consumption without one meter (to all meters)
    and it calculates the added risk to pass a certain threshold for any meter
    :param directory: the directory in which the primaries are found
    :param filename: the filename of the primaries csv file. (usualy primaries_simplified.csv)
    :return:
    """

    # lets read the primaries file and make sure the ownerId is read as a string
    df = pd.read_csv(f'{directory}\\{filename}')
    df['ownerId'] = df['ownerId'].astype(str)
    ownerIds = df['ownerId'].unique()

    # calculating the pivot tables to each meter
    pts_ind = {}
    if not os.path.exists(f"{directory}\\stations_agg"):
        os.mkdir(f"{directory}\\stations_agg")
    for counter, owner in enumerate(ownerIds):
        df_partial = df[df['ownerId'] == owner]
        pts_ind[owner] = pd.pivot_table(data=df_partial, values='prognoses', index='timeFrom', columns='modelId',
                                        aggfunc=np.sum)
        pts_ind[owner].to_csv(f"{directory}\stations_agg\\{owner}.csv")
        logging.info(f'done summarizing station {owner}. {counter}/{len(ownerIds)}')

    # calculating the aggregate pivot table and than subtracting the individual pt's from it to get the aggregate
    # without it
    pt = pd.pivot_table(data=df, values='prognoses', index='timeFrom', columns='modelId', aggfunc=np.sum)
    agg_without = {}
    if not os.path.exists(f"{directory}\\stations_agg_without"):
        os.mkdir(f"{directory}\\stations_agg_without")
    for counter, owner in enumerate(ownerIds):
        agg_without[owner] = pt.subtract(pts_ind[owner], fill_value=0)
        logging.info(f'done subtracting station {owner}. {counter}/{len(ownerIds)}')
        agg_without[owner].to_csv(f"{directory}\\stations_agg_without\\{owner}.csv", header=True)

    logging.info('done summarizing and subtracting')

    # we will need both of these values for the heatmap/probability map calculation, they will serve as our boundries
    max_val = pt.max().max() * 1.2
    min_val = pt.min().min() / 0.8

    # noinspection PyTypeChecker
    def integrate_cdf(row, minv=min_val, maxv=max_val, res=100):

        """
        this function integrates a cumulative probability based on a kde with a narrow bandwidth
        :param row: a collection of prediction from which it estimates the probability function
        :param minv: the lower boundary of our calculation
        :param maxv: the upper boundary of our calculation
        :param res: the resolution, the number of steps from minv to maxv
        :return: a row containing the cumulative probability for passing each threshold
        """
        val = row.dropna().values
        # chose a narrow bandwidth so the right tail would be thinner
        bw = 0.04
        kernel = gaussian_kde(val, bw_method=bw)
        space = np.linspace(minv, maxv, res)
        cumulative = [kernel.integrate_box_1d(0, value) for value in space]
        return 1 - pd.Series(cumulative)

    def make_discrete_cdf(row, minv=min_val, maxv=max_val, res=100):
        """
        the discrete version of the integrate_cdf function. for each point on our linspace, checks how many models
        predicted a higher value than itself
        :param row: a collection of prediction from which it estimates the probability function
         :param minv: the lower boundary of our calculation
        :param maxv: the upper boundary of our calculation
        :param res: the resolution, the number of steps from minv to maxv
        :return: a row containing the normalized discrete cumulative probability.
        """

        models = row.dropna().values
        space = np.linspace(minv, maxv, res)
        cumulative = pd.Series([(value < models).sum() for value in space])
        # lets not forget to normalize by dividng in the maximum value
        return cumulative / cumulative.max()

    # we can get the total probability map by integrating over the total pivot table
    all_risk = pt.apply(integrate_cdf, axis=1)
    # and renaming the columns. we can interpolate later for certain thresholds
    all_risk.columns = np.linspace(min_val, max_val, 100)

    logging.info("done assesing total risk")

    '''
    now for the heavier calculation. we shall calculate the cdf map for each aggregate without a certain meter,
    and subtract that from the total cdf map, making a difference map. we will take the maximum for each threshold,
    giving us the max risk added for each threshold by that meter.
    '''
    max_risk_diff = {}
    for counter, owner in enumerate(ownerIds):
        risk_without = agg_without[owner].apply(integrate_cdf, axis=1)
        risk_without.columns = np.linspace(min_val, max_val, 100)
        risk_diff = all_risk.subtract(risk_without, fill_value=0)
        max_risk_diff[owner] = risk_diff.max(axis=0)
        message = f'done assesing risk of station {owner}. {counter}/{len(ownerIds)}'
        logging.info(message)

    # compiling all of that information into a single table, and saving it for later
    max_risk_station = pd.DataFrame(max_risk_diff)
    max_risk_station.to_csv(f'{directory}\\added_risk_by_station_smooth.csv', header=True)
    logging.info('wrote smooth version')


if __name__ == '__main__':
    filepath = sys.argv[1]
    directory, filename = os.path.split(filepath)
    logging.basicConfig(filename=f'{directory}\\logfile.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    aggregate(directory, filename)
