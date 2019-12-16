# This program uses the Python wrapper for IRBEM-lib to make a 
# POES magepehem file with the T89 magnetic field model.

import netCDF4
import numpy as np
from datetime import datetime, timedelta
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates
import os

import IRBEM

def convert_time(data, verbose=True):

    """
    Convert the year, day, and msec columns into a more useful format. 
    We are using list comprehension. And this is slow.

    Parameters
    ----------
    data : netCDF4.Dataset()
        The POES data that contains the 'year', 'day' (day of year), 
        and 'msec' columns.
    verbose : bool, optional
        Print how long this code takes to run. Useful for debugging 
        purposes.       

    Returns
    -------
    t_array: list
        a list of datetime objects of length data['time']
    """
    if verbose: start_time = time.time()
    # This is a very annoying conversion...
    t_array = [datetime.strptime(f'{data["year"][i]}, {data["day"][i]}', '%Y, %j') + 
            timedelta(milliseconds=int(data['msec'][i]))
            for i in range(len(data['time'][:]))]

    if verbose: print(f'Run time {round(time.time() - start_time)} s')
    return np.array(t_array) # Cast to np.array for more functinality.

def run_irbem(t, data, mag_model='T89'):
    """
    Run IRBEM make_lstar to get the L and MLT values for the spacecraft positions 
    given in the data argument at time stamps 
    """
    model = IRBEM.MagFields(kext=mag_model)

    x = {'dateTime':t, 'x1':data['alt'][:], 'x2':data['lat'][:], 
        'x3':data['lon'][:]}
    
    if mag_model == 'OPQ77':
        maginput=None
    elif mag_model == 'T89':
        kp = get_kp_values(t)
        maginput = {'kp':kp}
    else:
        raise NotImplementedError

    model.make_lstar(x, maginput)
    L_OPQ = np.array(model.make_lstar_output['Lm'])
    MLT_OPQ = np.array(model.make_lstar_output['MLT'])
    return L_OPQ, MLT_OPQ

def get_kp_values(time_array):
    """
    Load in a kp file in the currect directory and for each 
    time in time_array find the first kp value before that 
    time. If not time is found within 3 hours, raise an error.
    """
    numerical_times = matplotlib.dates.date2num(time_array)

    df = pd.read_csv(f'./data/{time_array[0].year}_kp.csv') # Load in the kp times
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    kp_times = matplotlib.dates.date2num(df['dateTime'])
    matched_kp = np.nan*np.ones_like(numerical_times)

    for i, n_t in enumerate(numerical_times):
        idt = np.where(n_t >= kp_times)[0][-1]
        if ((time_array[i] - df['dateTime'][idt]).total_seconds()) > 3*3600:
            raise ValueError('Unable to find a kp value within 3 hours '
                              'of requested point')
        matched_kp[i] = df['kp'][idt]
    return matched_kp

def save_magephem(file_name, times, L, MLT, mag_model):
    """ Saves the magnetic ephemeris to a csv file in ./data/"""
    df = pd.DataFrame(data=np.stack((times, L, MLT), axis=1), 
                     columns=['dateTime', f'L_{mag_model}', f'MLT_{mag_model}'])
    df.to_csv(os.path.join('./data', file_name), index=False)
    return


if __name__ == '__main__':
    # Load in the POES data from the POES_DATA_PATH path.
    POES_DATA_PATH = './data/poes_m01_20180922_raw.nc'
    mag_model='T89'
    data = netCDF4.Dataset(POES_DATA_PATH)

    time_array = convert_time(data)
    L_OPQ, MLT_OPQ = run_irbem(time_array, data, mag_model=mag_model)

    # Make a save_name string by manipulating the POES_DATA_PATH
    save_name = os.path.basename(POES_DATA_PATH)
    split_name = save_name.split('.')
    split_name[0] = split_name[0]+'_magephem'
    save_name = split_name[0] + '.csv'
    print(f'Saving to {save_name}')

    save_magephem(save_name, time_array, L_OPQ, MLT_OPQ, mag_model)


    if True:
        fig, ax = plt.subplots(2, sharex=True)
        # Filter out -1E31 bad values e.g. open field lines in
        # the polar cap and then take the absolute value. The 
        # absolute value is useful if you don't need to know
        # if poes is in the bounce loss cone.
        idx_good = np.where(L_OPQ != -1E31)[0]
        L = np.abs(L_OPQ[idx_good])
        ax[0].plot(time_array[idx_good], L)
        ax[1].plot(time_array[idx_good], MLT_OPQ[idx_good])
        ax[0].set(ylabel=f'L_{mag_model}')
        ax[1].set(xlabel='UTC', ylabel=f'MLT_{mag_model}')
        plt.show()