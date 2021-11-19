

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




def alt_risk_rater(directory, filename):
    """
    rates the risk of stations based on their actual effect on the monthly maximum and on their daily maximum
    variance (actualy standard deviation)
    :param directory: the directory in which the actuals file is found
    :param filename: the actuals filename
    :return:
        """
    actuals = pd.read_csv(f'{directory}\\{filename}')

    # lets group by station
    pt_by_station = pd.pivot_table(data=actuals, values='energyKwh', index='timeFrom', columns='id')
    pt_by_station['total'] = pt_by_station.sum(axis=1)
    # and adjust for hourly consumption
    pt_by_station *= 2
    pt_by_station.index = pd.to_datetime(pt_by_station.index)
    
    # the following is a list of station ranked by the number of zero values they have
    stations_by_zero_values = (pt_by_station == 0).sum(axis=0).sort_values(ascending=False)

    # we would like to take out of our calculation any station that has more
    # than 500 zero values, as it would inappropriately be marked as 'safe'

    uncalculated_meters = stations_by_zero_values[stations_by_zero_values > 500].index

    # lets get the must-meters, the ones we have to include:
    # those are the ones we actualy use
    meters_used = actuals['id'].unique()

    # those are the ones we must used
    meters = pd.read_csv(f'..\\data\\OPC-Meters.csv')
    must_customers = pd.read_csv(f'..\\data\\must_meters.csv')
    must_station = [station for station in meters['name'].values for must in must_customers['Must Customers'].values if
                    must in station]
    must_meters = meters[meters['name'].isin(must_station)]['meterId'].values

    # this is their intersection
    must_meters_used = [meter for meter in must_meters if meter in meters_used]

    # lets drop them for the rating, as they will not be taken into account in it
    pt_by_station_to_rank = pt_by_station.drop(columns=must_meters_used).drop(columns=uncalculated_meters)

    # now lets rate the station by the amount they contribute to the total maximum

    effect_by_meter = {}
    for column in pt_by_station_to_rank.columns:
        max_without = (pt_by_station_to_rank['total'] - pt_by_station_to_rank[column]).max()
        effect_on_max = pt_by_station_to_rank['total'].max() - max_without
        effect_by_meter[column] = effect_on_max

    # and rate them by that risk without the 'total' column
    meters_by_risk = pd.Series(effect_by_meter).sort_values()[:-1]

    # doing the same for total consumption might also be right, that way
    # we can measure risk against importance again

    meters_by_consumption = pt_by_station_to_rank.sum()
    stations_risk_cons = pd.DataFrame(
        {'effect_on_max': pd.Series(effect_by_meter), 'consumption': meters_by_consumption})
    stations_risk_cons['ratio'] = stations_risk_cons['effect_on_max'] / stations_risk_cons['consumption']
    # lets save that
    stations_risk_cons.sort_values('ratio', ascending=False).to_csv('station_risk_consumption.csv')


    # additionaly we can extract their daily maximums and work with that
    daily_max = pt_by_station_to_rank.groupby(by=pt_by_station_to_rank.index.day).max()
    daily_max_std = daily_max.apply(np.std, axis=0)[:-1].sort_values()
    daily_max.to_csv('daily_maxes.csv', header=True)


    # finally, picking them by their total max effect until they get to a certain threshold
    rate = 400
    meters_included = must_meters_used
    for meter in meters_by_risk.index:
        current_max = pt_by_station[meters_included].sum(axis=1).max()
        if current_max > rate * 1000:
            break
        meters_included.append(meter)


    # and takning the least risky meters
    least_risky = meters_by_risk[len(meters_included):]
