# modificado por: Marcelo 1/18/2018
# modificado por: rayner mauricio 1/15/2018

# MODIFICAR A LISTA "pastas"!!!!!!!!!!

import os
import pandas as pd
import csv
import glob
from multiprocessing import Pool

BASE_DIR = os.getcwd()
ZONAS = ['1', '2', '3', 'SALA']


def filter_idf_files(files):
    idf_files = []

    for file in files:
        if str(file).endswith(".idf"):
            idf_files.append(file)

    return idf_files


def entradas_conforto(file, zona):
    
    menor16 = 0
    entre16e18 = 0
    entre18e23 = 0
    entre23e26 = 0
    maior26 = 0
    timesteps = 0

    if zona == 'SALA':

        try:
            timesteps = (file['SALA1:People Occupant Count [](TimeStep)'] > 0).value_counts()[True]
        except:
            timesteps = 0

        try:
            menor16 = ((file[zona+':Zone Operative Temperature [C](TimeStep)'] < 16) & (file['SALA:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            menor16 = 0

        try:    
            entre16e18 = ((file[zona+':Zone Operative Temperature [C](TimeStep)'] >= 16) & (file[zona+':Zone Operative Temperature [C](TimeStep)'] < 18) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre16e18 = 0
        
        try:
            entre18e23 = ((file[zona+':Zone Operative Temperature [C](TimeStep)'] >= 18) & (file[zona+':Zone Operative Temperature [C](TimeStep)'] < 23) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre18e23 = 0

        try:
            entre23e26 = ((file[zona+':Zone Operative Temperature [C](TimeStep)'] >= 23) & (file[zona+':Zone Operative Temperature [C](TimeStep)'] < 26) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre23e26 = 0    
        
        try:
            maior26 = ((file[zona+':Zone Operative Temperature [C](TimeStep)'] >= 26) & (file['SALA1:People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            maior26 = 0
    
    else:

        try:
            timesteps = (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0).value_counts()[True]
        except:
            timesteps = 0

        try:
            menor16 = ((file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] < 16) & (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            menor16 = 0
        
        try:
            entre16e18 = ((file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] >= 16) & (file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] < 18) & (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre16e18 = 0

        try:
            entre18e23 = ((file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] >= 18) & (file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] < 23) & (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre18e23 = 0

        try:
            entre23e26 = ((file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] >= 23) & (file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] < 26) & (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            entre23e26 = 0

        try:    
            maior26 = ((file['DORM'+zona+':Zone Operative Temperature [C](TimeStep)'] >= 26) & (file['DORMITORIO'+zona+':People Occupant Count [](TimeStep)'] > 0)).value_counts()[True]
        except:
            maior26 = 0
    
    return [menor16, entre16e18, entre18e23, entre23e26, maior26, timesteps]


def processar_pasta(pasta):
    # os.chdir(BASE_DIR+'\\'+pasta)  # ugly looking mess for windows users
    os.chdir(BASE_DIR+'/'+pasta)
    files = os.listdir(os.getcwd())
    files.sort()
    idf_files = filter_idf_files(files)

    dados = {}
    dados['pasta'] = []
    dados['arquivo'] = []
    dados['zona'] = []
    dados['heating'] = []
    dados['cooling'] = []
    dados['menor16'] = []
    dados['entre16e18'] = []
    dados['entre18e23'] = []
    dados['entre23e26'] = []
    dados['maior26'] = []
    dados['timesteps'] = []

    for file in idf_files:
        
        print(file)
        openfile = pd.read_csv(file[:-4]+'.csv')
        
        for zona in ZONAS:
            
            if zona == 'SALA':
                heatingkey = (zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)')
                coolingkey = (zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)')
            else:
                heatingkey = ('DORM'+zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)')
                coolingkey = ('DORM'+zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)')

            heatingIdealLoads = sum(openfile[heatingkey])
            coolingIdealLoads = sum(openfile[coolingkey])
                
            horas = entradas_conforto(openfile, zona)  # fracao de horas
                
            dados['pasta'].append(pasta)
            dados['arquivo'].append(file)
            dados['zona'].append(zona)
            dados['heating'].append(heatingIdealLoads)
            dados['cooling'].append(coolingIdealLoads)
            dados['menor16'].append(horas[0])
            dados['entre16e18'].append(horas[1])
            dados['entre18e23'].append(horas[2])
            dados['entre23e26'].append(horas[3])
            dados['maior26'].append(horas[4])
            dados['timesteps'].append(horas[5])

    df = pd.DataFrame(dados)
    df.to_csv('dados_{}.csv'.format(pasta))


if __name__ == '__main__':
    # pastas = ['BeloHorizonte', 'FozdoIguacu', 'Goiania', 'Niteroi', 'RiodeJaneiro']
    pastas = glob.glob('_*')

    print('Processing {} folders in \'{}\':'.format(len(pastas), BASE_DIR))
    for pasta in pastas:
        print('\t{}'.format(pasta))

    threaded = True
    # threaded = False

    if threaded:
        num_pastas = len(pastas)
        p = Pool(num_pastas)
        print(p.map(processar_pasta, pastas))
    else:
        for pasta in pastas:
            processar_pasta(pasta)
