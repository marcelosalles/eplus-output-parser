"""
Created to resume the output variables from EnergyPlus to one line in a data frame.

It takes from the output variables file, for each zone:
    - the numbers of timesteps with occupation;
    - the numbers of timesteps below 16 degrees with occupation;
    - the numbers of timesteps between 16 and 18 degrees with occupation;
    - the numbers of timesteps between 18 and 23 degrees with occupation;
    - the numbers of timesteps between 23 and 26 degrees with occupation;
    - the numbers of timesteps above 26 degrees with occupation;
    - the numbers of timesteps without HVAC on, with occupation;
    - the sum of the Zone Ideal Loads Supply Air Total Heating Energy;
    - the sum of the Zone Ideal Loads Supply Air Total Cooling Energy.

*Programa criado para resumir os output variables do EnergyPlus em uma linha de data frame.
"""

import os
import pandas as pd
import csv
import glob
from multiprocessing import Pool
import datetime
import argparse

BASE_DIR = os.getcwd()

# ZONES is golbal variable. It will only work when the model has the same number of zones with the same names.
ZONES = ['1', '2', '3', 'SALA']


def filter_idf_files(files):
    #Filters the files in the folder to take only .idf files

    idf_files = []

    for file in files:
        if str(file).endswith(".idf"):
            idf_files.append(file)

    return idf_files


def inputs_comfort(file, zone):
    #It counts the numeber of timesteps, and divides the Operative Temperature in bands 
    
    less16 = 0
    from16to18 = 0
    from18to23 = 0
    from23to26 = 0
    more26 = 0
    timesteps = 0

    if zone == 'SALA':

        try:
            timesteps = (file['SALA1:People Occupant Count [](TimeStep)'] > 0).value_counts()[True]
        except:
            timesteps = 0

        try:
            less16 = ((file[zone+':Zone Operative Temperature [C](TimeStep)'] < 16) & (file['SALA:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            less16 = 0

        try:    
            from16to18 = ((file[zone+':Zone Operative Temperature [C](TimeStep)'] >= 16) & (file[zone+':Zone Operative Temperature [C](TimeStep)'] < 18) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from16to18 = 0
        
        try:
            from18to23 = ((file[zone+':Zone Operative Temperature [C](TimeStep)'] >= 18) & (file[zone+':Zone Operative Temperature [C](TimeStep)'] < 23) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from18to23 = 0

        try:
            from23to26 = ((file[zone+':Zone Operative Temperature [C](TimeStep)'] >= 23) & (file[zone+':Zone Operative Temperature [C](TimeStep)'] < 26) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from23to26 = 0    
        
        try:
            more26 = ((file[zone+':Zone Operative Temperature [C](TimeStep)'] >= 26) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            more26 = 0
    
    else:

        try:
            timesteps = (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0).value_counts()[True]
        except:
            timesteps = 0

        try:
            less16 = ((file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] < 16) & (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            less16 = 0
        
        try:
            from16to18 = ((file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] >= 16) & (file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] < 18) & (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from16to18 = 0

        try:
            from18to23 = ((file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] >= 18) & (file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] < 23) & (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from18to23 = 0

        try:
            from23to26 = ((file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] >= 23) & (file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] < 26) & (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            from23to26 = 0

        try:    
            more26 = ((file['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] >= 26) & (file['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            more26 = 0
    
    return [less16, from16to18, from18to23, from23to26, more26, timesteps]


def process_folder(folder):
    #Takes the output variables file, and resumes the data into a dict.

    os.chdir(BASE_DIR+'/'+folder)
    files = os.listdir(os.getcwd())
    files.sort()
    idf_files = filter_idf_files(files)

    data = {}
    data['folder'] = []
    data['file'] = []
    data['zone'] = []
    data['heating'] = []
    data['cooling'] = []
    data['less16'] = []
    data['from16to18'] = []
    data['from18to23'] = []
    data['from23to26'] = []
    data['more26'] = []
    data['timesteps'] = []
    data['HVAC free hours'] = []

    for file in idf_files:
        
        openfile = pd.read_csv(file[:-4]+'.csv')
        
        for zone in ZONES:
            
            if zone == 'SALA':

                try:
                    hcomf = ((openfile['HVAC_SALA:Schedule Value [](TimeStep)'] == 0) & (openfile['SALA:People Occupant Count [](TimeStep)'] > 0) & (openfile[zone+':Zone Operative Temperature [C](TimeStep)'] >= 18)).value_counts()[True]
                except:
                    hcomf = 0
                heatingkey = zone + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)'
                coolingkey = zone + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)'
            
            else:

                try:
                    hcomf = ((openfile['HVAC_DORM'+zone+':Schedule Value [](TimeStep)'] == 0) & (openfile['DORMITORIO'+zone+':People Occupant Count [](TimeStep)'] > 0) & (openfile['DORM'+zone+':Zone Operative Temperature [C](TimeStep)'] >= 18)).value_counts()[True]
                except:
                    hcomf = 0
                heatingkey = 'DORM' + zone + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)'
                coolingkey = 'DORM' + zone + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)'

            try:
                heatingIdealLoads = sum(openfile.get(heatingkey))
            except:
                heatingIdealLoads = 'NULL'
            
            try:
                coolingIdealLoads = sum(openfile.get(coolingkey))
            except:    
                coolingIdealLoads = 'NULL'

            horas = inputs_comfort(openfile, zone)
                
            data['folder'].append(folder)
            data['file'].append(file)
            data['zone'].append(zone)
            data['heating'].append(heatingIdealLoads)
            data['cooling'].append(coolingIdealLoads)
            data['less16'].append(horas[0])
            data['from16to18'].append(horas[1])
            data['from18to23'].append(horas[2])
            data['from23to26'].append(horas[3])
            data['more26'].append(horas[4])
            data['timesteps'].append(horas[5])
            data['HVAC free hours'].append(hcomf)

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

        if len(folders) > 8:
            num_threads = 8
            print('Multi thread process... \n','Number of threads: 8')

        else:            

            num_threads = len(folders)
            print('Multi thread process... \n','Number of threads: ',num_threads)

        num_threads = len(folders)
        p = Pool(num_threads)
        p.map(process_folder, folders)

    else:

        print('Single thread process...')
        for folder in folders:
            process_folder(folder)

    end_time = datetime.datetime.now()

    total_time = (end_time - start_time)
    print("Total time: " + str(total_time))
