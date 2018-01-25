"""

Counts the occupied hours in a zone where no need for HVAC is required.

"""

import os
import pandas as pd
import csv
import glob
from multiprocessing import Pool
import datetime
import argparse

BASE_DIR = os.getcwd()
ZONES = ['1', '2', '3', 'SALA']


def filter_idf_files(files):
    idf_files = []

    for file in files:
        if str(file).endswith(".idf"):
            idf_files.append(file)

    return idf_files

def process_folder(folder):
    # os.chdir(BASE_DIR+'\\'+folder)  # ugly looking mess for windows users
    os.chdir(BASE_DIR+'/'+folder)
    files = os.listdir(os.getcwd())
    files.sort()
    idf_files = filter_idf_files(files)

    data = {}
    data['folder'] = []
    data['file'] = []
    data['zone'] = []
    data['HVAC free hours'] = []

    for file in idf_files:
        
        print('Processing file ',file, end = '\r')

        openfile = pd.read_csv(file[:-4]+'.csv')
        
        for zone in ZONES:

            if zone == 'SALA':
                try:
                    hconf = ((openfile['HVAC_SALA:Schedule Value [](TimeStep)'] == 0) & (openfile['SALA:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
                except:
                    hconf = 0

            else:
                try:
                    hconf = ((openfile['HVAC_DORM'+zone+':Schedule Value [](TimeStep)'] == 0) & (openfile['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
                except:
                    hconf = 0
                
            data['folder'].append(folder)
            data['file'].append(file)
            data['zone'].append(zone)
            data['HVAC free hours'].append(hconf)

    df = pd.DataFrame(data)
    df.to_csv('dados{}.csv'.format(folder))
    print('\tDone processing folder \'{}\''.format(folder))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process output data from Energyplus.')
    parser.add_argument('-t',
                        action='store_false',
                        help='run a thread pool equal to the number of eligible folders')
    args = parser.parse_args()
    threaded = args.t

    folders = glob.glob('_*')

    print('Processing {} folders in \'{}\':'.format(len(folders), BASE_DIR))
    for folder in folders:
        print('\t{}'.format(folder))

    start_time = datetime.datetime.now()

    if threaded:
        print('Multi thread process')
        num_folders = len(folders)
        p = Pool(num_folders)
        p.map(process_folder, folders)
    else:
        print('Single thread process')
        for folder in folders:
            process_folder(folder)

    end_time = datetime.datetime.now()

    total_time = (end_time - start_time)
    print("Total time: " + str(total_time))
