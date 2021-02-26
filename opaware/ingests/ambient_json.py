import json
import numpy as np
import pandas as pd
import xarray as xr


def ingest_915_jsons(my_data):
    dates = np.array([pd.to_datetime(element['time']) for element in my_data])
    ordd = dates.argsort()
    dates = dates[ordd].astype('datetime64[ns]')

    mapn = {'temperature_C': 'outside_temperature',
            'humidity': 'humidity',
            'rain_mm': "total_rainfall",
            'light_lux': "solar_lux",
            'wind_dir_deg': 'wind_direction',
            'wind_avg_m_s': 'wind_speed',
            'wind_max_m_s': 'max_wind_speed',
            'uvi': 'uv_index',
            'uv': 'UV'}

    dont_care = ['time', 'loc', 'lastRain', 'tz', 'macAddress', 'battery_ok', 'model', 'id', 'mic', 'uv']
    numpy_data = {}
    for variable in list(my_data[0].keys()):
        if variable not in dont_care:
            # print(variable)
            vim = []
            for element in my_data:
                vim.append(element[variable])
            this = np.array(vim)

            # this = np.array([element[variable] for element in my_data])[ordd]
            numpy_data.update({mapn[variable]: (['time'], this)})

    tu = 'C'
    tsn = 'Temperature'
    # dpsn = 'Dewpoint'
    xds = xr.Dataset(numpy_data,
                     coords={'time': dates})

    # xds['inside_temperature'].attrs = {'standard_name' : tsn, 'units' : tu, 'long_name' : 'inside_temperature'}
    xds['outside_temperature'].attrs = {'standard_name': tsn, 'units': tu, 'long_name': 'outside_temperature'}
    # xds['outside_dewpoint'].attrs = {'standard_name' : dpsn, 'units' : tu, 'long_name' : 'outside dewpoint'}
    # xds['inside_dewpoint'].attrs = {'standard_name' : dpsn, 'units' : tu, 'long_name' : 'inside dewpoint'}
    xds['total_rainfall'].attrs = {'standard_name': 'rainfall', 'units': 'mm', 'long_name': 'Total Rainfall'}
    xds.attrs['datastream'] = 'Beer And Bike Barn Met Station'

    return xds


def ingest_ambient(textlines):
    """
    Ingest Ambient text stream collected from rtl_433 to an
    ACT compliant xarray object

    Parameters
    ----------
    textlines : list
        A list of text formatted as JSONs to be converted


    Returns
    -------
    data : ACT xarray object
        ACT object with data contaied

    Examples
    --------
    TBD
    """

    jdatas = []
    for this in textlines:
        try:
            tjs = json.loads(this)
            jdatas.append(tjs)
        except json.JSONDecodeError:
            print(this)

    first_WH24 = True
    first_WH65B = True
    good_jdatas = []
    for dat in jdatas:
        if 'WH65B' in dat['model']:
            if first_WH65B:
                start_rain_65 = float(dat['rain_mm'])
                dat['rain_mm'] = 0.
                first_WH65B = False
            else:
                dat['rain_mm'] = (float(dat['rain_mm']) - start_rain_65)
            good_jdatas.append(dat)
        if 'WH24' in jdatas:
            if first_WH24:
                start_rain_24 = float(dat['rain_mm'])
                dat['rain_mm'] = 0
                first_WH24 = False
            else:
                dat['rain_mm'] = (float(dat['rain_mm']) - start_rain_24)
            good_jdatas.append(dat)

    really_good = []
    for i in range(len(good_jdatas)):
        if 'uvi' in good_jdatas[i].keys():
            really_good.append(good_jdatas[i])

    mxr = ingest_915_jsons(really_good)
    mxr['solar_irrad'] = mxr['solar_lux'] * 0.0079
    td = 243.04 * (np.log(mxr['humidity'] / 100.)
                   + ((17.625 * mxr['outside_temperature']) / (243.04 + mxr['outside_temperature']))) / (
                     17.625 - np.log(mxr['humidity'] / 100)
                     - ((17.625 * mxr['outside_temperature']) / (243.04 + mxr['outside_temperature'])))

    mxr['outside_dewpoint'] = td
    tu = 'F'
    # tsn = 'Temperature'
    dpsn = 'Dewpoint'
    mxr['outside_dewpoint'].attrs = {'standard_name': dpsn, 'units': tu, 'long_name': 'outside dewpoint'}

    rollings = mxr.rolling(time=10, center=True).mean()
    mxr['mean_wind_dir'] = rollings['wind_direction']
    mxr['mean_wind_speed'] = rollings['wind_speed']

    return mxr
