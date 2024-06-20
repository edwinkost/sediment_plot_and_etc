import os 
import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import transforms
#import geopandas as gpd


import os 
import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import transforms
import numpy as np
#import geopandas as gpd



def read_observations_and_estimations(inputdir, obsfile, estfile):
    """
        Compares observation data and estimations from csv files.
    """
    dateparse_est = lambda x: pd.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    #dateparse = lambda x: pd.datetime.strptime(x,'%m')
   
    #dateparse_obs = lambda x: pd.datetime.strptime(x,'%d-%m-%Y %H:%M')
    dateparse_obs = lambda x: pd.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')


    obs_inputdata = pd.read_csv(
        os.path.join(inputdir, obsfile),
        parse_dates = [0],
        date_parser = dateparse_obs,
        delimiter=";"
    )
    
    est_inputdata = pd.read_csv(
        os.path.join(inputdir, estfile),
        parse_dates = [0],
        date_parser = dateparse_est,
        delimiter=","
    )
    est_inputdata.rename(columns = {"Unnamed: 0" : "Date"}, inplace = True)
    print(est_inputdata.head())
    
    # Add these lines to replace 0 with empty cell
    for column in obs_inputdata.select_dtypes(include=['number']).columns:
        obs_inputdata[column] = obs_inputdata[column].replace(0, '')
    
    #obs_inputdata.replace(0, '', inplace=True)
    obs_inputdata["date"] = obs_inputdata['date'] = pd.to_datetime(obs_inputdata['date']).dt.normalize()
    est_inputdata["Date"] = est_inputdata['Date'] = pd.to_datetime(est_inputdata['Date']).dt.normalize()

     # Set the day to the 15th
    obs_inputdata["date"] = obs_inputdata["date"].apply(lambda x: x.replace(day=15))
    est_inputdata["Date"] = est_inputdata["Date"].apply(lambda x: x.replace(day=15))


    print(obs_inputdata)
    print(est_inputdata)

    obs_inputdata["month-year-day"] = pd.to_datetime(
        obs_inputdata['date'],
        errors='coerce'
    ).dt.to_period('D')
    est_inputdata["month-year-day"] = pd.to_datetime(
        est_inputdata['Date'],
        errors='coerce'
    ).dt.to_period('D')

    
    print('the observations and estimations are after overwriting', obs_inputdata.head(),est_inputdata.head())

    return obs_inputdata, est_inputdata
#fed

def compare_observations_and_estimations(inputdir, outputdir, obsfile, estfile,outfile):
    """
        Compares observation data and estimations from csv files.
    """
    obs_input, est_input = read_observations_and_estimations(inputdir, obsfile, estfile)
    #obs_est_merged = pd.merge(obs_input, est_input, on=['month'], how='left')
    obs_est_merged = pd.merge(obs_input, est_input, on=['month-year-day'], how='left')
    obs_est_merged.drop(['Date'], axis=1, inplace=True)
    print('the columns of the merged file are', obs_est_merged.columns.to_list())
    # put the Date column in a first position
    my_first_column = obs_est_merged.pop('month-year-day')
    #print(my_first_column)
    #my_first_column = obs_est_merged.pop('month')
    #obs_est_merged.insert(0, 'month', my_first_column)
    obs_est_merged.insert(0, 'month-year-day', my_first_column)
    # delete certain columns
    
    #obs_est_merged.drop(['Date_x', 'Date_y'], axis=1, inplace=True)
    print('the merged file is', obs_est_merged.head())

    obs_est_merged.to_csv(os.path.join(outputdir, outfile))
#fed

def compare_observations_and_estimations_per_station(inputdir, outputdir, obsfile, estfile, outname, station_names):
    """
        Compares observation data and estimations from csv files on a per station basis and
        plots the result and saves it to the output file.
    """
    obs_input, est_input = read_observations_and_estimations(inputdir, obsfile, estfile)
    fig, ax = plt.subplots(4, 2, sharex= False,figsize=(15,15))

    for i, station_name in enumerate(station_names):
        obs_station = obs_input[[station_name,'month-year-day']]
        #obs_station = obs_input[[station_name,'month']]
        est_station = est_input[[station_name,'month-year-day']]
        #est_station = est_input[[station_name,'month']]
        obs_station.rename(columns = {station_name : station_name + "_obs"}, inplace = True)
        est_station.rename(columns = {station_name : station_name + "_est"}, inplace = True)
        station = pd.merge(obs_station, est_station, on=['month-year-day'], how='left')
        station.rename(columns = {'month-year-day':'year' }, inplace = True)
        station.replace('', np.nan, inplace=True)
        station.dropna(inplace=True)
        print('the station values are after dropping the empty rows',station)
        #station = station.drop_duplicates(subset=['month-year'], keep='first')
        #station = pd.merge(obs_station, est_station, on=['month'], how='left')
        print('the merged file is', station.head())
        # put the Date column in a first position
        my_first_column = station.get('year')
        #my_first_column = station['month']
        station.index = my_first_column
        print('the station index is', station.index)
        
        if station_name == 'SERRINHA':
         # Convert the observation column to numeric, coercing errors to NaN
            station[station_name + "_obs"] = pd.to_numeric(station[station_name + "_obs"], errors='coerce')
    
            # Remove rows where the observation exceeds the threshold
            indexnames = station[station[station_name + '_obs'] > 10000000000].index
            print("Removing rows for:", indexnames)
            station.drop(indexnames, inplace=True)
        #if station_name == 'SERRINHA':
            #indexnames = station[station['SERRINHA_obs'] > 10000000000].index
            #print("Removing rows for: " , indexnames)
            #station.drop(indexnames, inplace=True)
        
        row = int(i/2)
        col = i%2
        
        print(i, row, col)
        
        #print(station.head())
        station.plot(ax=ax[row, col])
        
        ax[row,col].set_xlabel("year", fontsize=16)
        if col == 0:
            ax[row,col]
        ax[3,1].set_visible(False)
        ax[3,0].set_xlabel("year", fontsize=16)
        ax[0,0].set_xlabel("")
        ax[1,0].set_xlabel("")
        ax[2,0].set_xlabel("")
        ax[0,1].set_xlabel("")
        ax[1,1].set_xlabel("")
        ax[2,1].set_xlabel("year", fontsize=16)

        fig.text(0.06, 0.5, 'Monthly sediment transport (kg/month)', ha='center', va='center', rotation='vertical',fontsize=16)
        plt.savefig(os.path.join(outputdir, "figure_sed_new_lakes_data_updated.png"), format="png", dpi=300)
        station.to_csv(os.path.join(outputdir, f"{outname}_{station_name}_{'sed_new_lakes_data_updated'}.csv"))
    #rof
#fed

def run_obs_est_sed(inputDirPath, outputDirPath, obsFilename, estFilename):
    compare_observations_and_estimations(
        inputDirPath,
        outputDirPath,
        obsFilename,
        estFilename,
        'obs_est_sed_new_lakes_data_new_file.csv'
        )

    compare_observations_and_estimations_per_station(
        inputDirPath,
        outputDirPath,
        obsFilename,
        estFilename,
        'obs_est_sed_new_lakes_data_new_file.csv',
        ["OBIDOS_PORTO", "FAZENDAVISTAALEGRE", "PORTOVELHO", "SERRINHA", "MANACAPURU",
        "CARACARAI","TABATINGA"]
       
    )

    
if __name__ == "__main__":
    #print("Don't run this script on its own. Call the run_obs_est_sed function.")
    run_obs_est_sed('/scratch/naffa002/output-validation/old_run/old_run/hybam/',
                           '/scratch/naffa002/output-validation/old_run/old_run/hybam/sed_delivery/30years/paper/est_obs_tables_figures/',\
                            'monthly_observation_sediment_updated.csv',\
                           'sedimentTransport_from_sedimentTransport_monthly_new_lakes_data_new_stations_location.csv')