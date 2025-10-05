import pandas as pd
import numpy as np
import pandasgui
import matplotlib.pyplot as plt

data = pd.read_csv('dataset/population_by_country_2019_2020.csv')

print(data.head())
pandasgui.show(data)
data['Net population change'] = data['Population (2020)'] - data['Population (2019)']
data['Population change %'] = (data['Net population change'] / data['Population (2019)']) * 100
