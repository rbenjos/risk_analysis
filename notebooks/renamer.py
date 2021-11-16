def meter_to_name(directory,meterId):
    meters = pd.read_csv(f'{}\\..\\OPC-Meters.csv')
    name = meters.loc[meters['meterId'] == meterId]['name']
    if len(name) == 0:
        return meterId
    return name.values[0]w