# modificado por: Marcelo 1/18/2018
# modificado por: rayner mauricio 1/15/2018

# MODIFICAR A LISTA "pastas"!!!!!!!!!!

import os
import pandas as pd
import csv
import glob

dir = os.getcwd()

# A lista pastas deve ser atualizada de acordo com os nomes das cidades simuladas
#pastas = ['BeloHorizonte', 'FozdoIguacu', 'Goiania', 'Niteroi', 'RiodeJaneiro'] 
pastas = glob.glob('_*')

zonas = ['1', '2', '3', 'SALA']

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

def take_idf(files):
    idf_files = []

    for file in files:
        if str(file).endswith(".idf"):
            idf_files.append(file)

    return idf_files

def horasConforto(file,zona):
    
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
    
    return(menor16,entre16e18,entre18e23,entre23e26,maior26,timesteps)


for pasta in pastas:

    os.chdir(dir+'\\'+pasta)
    files = os.listdir(os.getcwd())
    files.sort()
    idf_files = take_idf(files)

    for file in idf_files:
        
        print(file)
        
        file = file[:-4]
        openfile = pd.read_csv(file+'.csv')
        
        for zona in zonas:
            
            if zona == 'SALA':
                
                heatingkey = (zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)')
            else:
                heatingkey = ('DORM'+zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Energy [J](TimeStep)')
            heatingIdealLoads = sum(openfile[heatingkey])
                
            if zona == 'SALA':
                
                coolingkey = (zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)')
            else:
                coolingkey = ('DORM'+zona + ' IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Cooling Energy [J](TimeStep)')
            
            coolingIdealLoads = sum(openfile[coolingkey])
                
            horas = horasConforto(openfile,zona) # fracao de horas
                
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
        
#print(dados)

os.chdir(dir)
df = pd.DataFrame(dados)

df.to_csv('dados.csv')