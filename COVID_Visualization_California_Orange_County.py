import math
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as grid

covid_url  = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/"
covid_file = "time_series_covid19_confirmed_US.csv"

spec = grid.GridSpec(ncols=2, nrows=1, width_ratios=[1,1])
fig = plt.figure(figsize=(15,6))
mapGraph = fig.add_subplot(spec[0])
barGraph = fig.add_subplot(spec[1])

covidMap = pd.read_csv(covid_url + covid_file, delimiter=",")
covidMap = covidMap.rename(columns = {'Admin2': 'County'})
covidMap = covidMap.set_index('County')
covidMap = covidMap.rename(columns = {'Province_State': 'State'})
covidMap = covidMap.rename(columns = {'Long_': 'longitude'})
covidMap = covidMap.rename(columns = {'Lat': 'latitude'})
covidMap = covidMap.rename(columns = {'11/8/21': 'deaths'})

covidMap["scaled_deaths"] = covidMap["deaths"] /100
caliCounties = covidMap['State'] == 'California'
caliMap = covidMap[caliCounties]
california = mpimg.imread('california.png')

mapGraph.scatter(caliMap["longitude"], caliMap["latitude"], s=caliMap["scaled_deaths"],
            label="Number of Deaths", alpha=0.4)
mapGraph.legend(fontsize=14)

mapGraph.imshow(california, extent=[-124.55, -113.80, 32.45, 42.05])
#mapGraph.set_ylabel("Latitude", fontsize=16, labelpad=15)
#mapGraph.set_xlabel("Longitude", fontsize=16, labelpad=15)
mapGraph.set_title("California Covid Deaths by County", fontsize=18, pad=15)
#END OF MAP GRAPH
#START OF BAR GRAPH
covid = pd.read_csv(covid_url + covid_file, delimiter=",")

covid = covid.rename(columns={"Admin2":"County", "Province_State":"State"})
covid = covid[covid["State"] == "California"]
covid = covid.set_index("County")

unused_columns = ["UID", "iso2", "iso3", "code3", "FIPS", "Long_", "Lat", "Country_Region", "Combined_Key", "State"]
covid = covid.drop(columns=unused_columns)

y_vals = covid.loc['Orange'] #has deaths of Orange county

x_vals = covid.loc["Orange"].index
x_vals = [datetime.strptime(day, '%m/%d/%y') for day in x_vals]

def get_total_deaths(pseries):
    total = 0
    for i in pseries:
        total += i
    return total

last_col = covid.shape[1]-1 #turns cumulative deaths into daily deaths
for col in range(last_col, 0, -1):
    covid.iloc[:,col] = covid.iloc[:,col] - covid.iloc[:,col-1]

daily_total_deaths = []
for i in covid:
    daily_total_deaths.append(get_total_deaths(covid[i]))

last = covid.shape[1] #7 day rolling average
for pos in range(7, last):
    covid.iloc[:,pos] = covid.iloc[:,(pos-6):(pos+1)].sum(axis=1)
    covid.iloc[:,pos] = covid.iloc[:,pos] / 7
    covid.iloc[:,pos] = round(covid.iloc[:,pos], 1)

caliTotal = 0
for i in daily_total_deaths:
    caliTotal += i

orangeTotal = 0
for i in y_vals:
    orangeTotal += i
totalOrange = 'Orange County Total: ' + str(orangeTotal)
totalCali = 'California Total: ' + str(caliTotal)
y_rolling = covid.loc["Orange"]
x_rolling = covid.loc["Orange"].index
x_rolling = [datetime.strptime(day, '%m/%d/%y') for day in x_rolling]
barGraph.plot(x_vals, y_vals, "-", color="orangered", label= totalOrange)
barGraph.plot(x_vals, daily_total_deaths, "-", color="lightsteelblue", label= totalCali)
barGraph.plot(x_rolling, y_rolling, "-", color="yellow")
barGraph.legend(loc='upper left')
barGraph.fill_between(x_vals, daily_total_deaths, color="lightsteelblue")
barGraph.fill_between(x_vals, y_vals, color="orangered")
barGraph.set_title("Daily COVID-19 Cases in California", fontsize=14, pad=15)
barGraph.set_title("COVID-19 Deaths in Orange County", fontsize=14, pad=15)
plt.show()
