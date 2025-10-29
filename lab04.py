import pandas as pd
import pandasgui
import matplotlib 
matplotlib.use('Qt5Agg')  # Backend interaktywny
import matplotlib.pyplot as plt
import numpy as np

# W tabeli przestawnej mogę wskazać kolumnę której elementy stworzą nowe kolumny
# Wektoryzacja- dążenie do tego aby operacje na całym zbiorze były efektywne
# Kiedy chcemy przepisać tabele po wartości a nie po indeksie musimy zamienić DataFrame na numpy array za pomocą .values

def task1():
    df = pd.read_csv('dataset/city_temperature.csv')

    temperature_by_region = df.groupby(['Region'])['AvgTemperature'].agg(['mean', 'min', 'max'])

    print(temperature_by_region)

    temperature_by_month = df.groupby(['Month'])['AvgTemperature'].agg(['mean', 'min', 'max'])

    print(temperature_by_month)

    pandasgui.show(df)

def task2():
    data = pd.read_csv('dataset/city_temperature.csv')
    # df = data.drop(columns=['Day']).pivot_table(columns='Region', index=['Year','Month'], aggfunc=['min', 'max', 'mean'], values='AvgTemperature' )
    df = data.drop(columns=['Day']).pivot_table(columns='Region', index=['Year', 'Month'], values='AvgTemperature')
    df = df.loc[(slice(None),[6, 12]),:]  # select only December and June
    df = df.drop(df.loc[([200, 201], slice(None)),:].index)
    # pandasgui.show(df)

    fig, axs = plt.subplots(2, 1, figsize=(8, 10))

    # Plot each region separately
    for region in df.columns:
        june_data = df.loc[(slice(None), 6), region].dropna()
        december_data = df.loc[(slice(None), 12), region].dropna()
        axs[0].plot(june_data.index.get_level_values(0), june_data.values, '.-', label=f'{region}')
        # axs[0].set_xticks(june_data.index.get_level_values(0).unique())
        axs[1].plot(december_data.index.get_level_values(0), december_data.values, '.-', label=f'{region}')
        # axs[1].set_xticks(december_data.index.get_level_values(0).unique())

    axs[0].legend(fontsize='small')
    axs[0].set_xlabel('Year')
    axs[0].set_ylabel('Average Temperature')
    axs[0].set_title('Temperature by Region - June')
    axs[1].legend(fontsize='small')
    axs[1].set_xlabel('Year')
    axs[1].set_ylabel('Average Temperature')
    axs[1].set_title('Temperature by Region - December')
    plt.show()

def task3():
    ecg = pd.read_csv('dataset/raw_ecg.csv')
    ecg_beats = pd.read_csv('dataset/ecg_beats.csv') # R indices
    R_val = ecg.iloc[ecg_beats.iloc[:, 0].astype(int), 1] # get R values using iloc

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ecg.iloc[:, 0], ecg.iloc[:, 1], label='Raw ECG Signal') # iloc[rows, columns]
    ax.plot(ecg_beats.iloc[:, 0], R_val, 'ro', label='Detected Beats')
    plt.show()

    signal_example = ecg['LeadI'].values
    event_timestamps = ecg_beats.iloc[:, 0].values

    sample_rate = 500 # Hz
    window_start = -0.55  # Start 550 ms before the event
    window_end = 0.4  # End 400 ms after the event

    time_vector = np.linspace(window_start, window_end, int((window_end - window_start) * sample_rate)+1)

    indices = (event_timestamps[:, np.newaxis] + sample_rate * time_vector).astype(int)
    clipped_indices = np.clip(indices, 0, len(signal_example) - 1)

    segments = signal_example[clipped_indices]

    average_signal = np.mean(segments, axis=0)
    print(average_signal)
    
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(time_vector, average_signal, label='Average ECG Beat')
    plt.show()
    plt.ion()

    print (f'Amplitude of the average beat: {np.max(average_signal)}')

    



def quiz():
    data = pd.read_csv('dataset/city_temperature.csv')
    df = data.drop(columns=['Day']).pivot_table(columns='Region', index=['Year','Month'], aggfunc=['min', 'max', 'mean'], values='AvgTemperature' )
    # df = data.drop(columns=['Day']).pivot_table(columns='Region', index=['Year', 'Month'], values='AvgTemperature')
    df = df.loc[:, (['min','max'],['Africa'])]  # select only Africa
    pandasgui.show(df)

def task4():
    data = pd.read_csv('dataset/titanic_train.csv')
    survived_data = data[data['Survived'] == 1]
    table_survived = survived_data.pivot_table(columns=['Sex'], index=['Pclass'], values=['PassengerId'], aggfunc='count')
    table_all = data.pivot_table(columns=['Sex'], index=['Pclass'], values=['PassengerId'], aggfunc='count')
    percentage = (table_survived / table_all) * 100
    pandasgui.show(percentage)
    # x = np.linspace(0, 1, 6)
    # fig, ax = plt.subplots(figsize=(8, 6))
    # # values = (table_survived.values / table_all.values).flatten()
    # x = np.arange(len(percentage.values.flatten()))
    # width = 0.3

    # ax.bar(x-width/2, percentage.loc[:,(slice(None), 'male')], width, label='Man')
    # ax.bar(x+width/2, percentage.loc[:,(slice(None), 'female')], width, label='Woman')

    # plt.show()

if __name__ == '__main__':
    task4()
