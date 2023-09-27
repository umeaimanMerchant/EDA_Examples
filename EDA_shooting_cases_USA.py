# -*- coding: utf-8 -*-
"""
EDA on shooting_rates in the USA

cover following process
- data cleaning
- creating variables
- structing 
- joining dataset
- validating
- presenting (visualization)

@author: UMEAIMAN

"""
# import lib
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)

#import dataset
df = pd.read_csv('C:/Users/AIMAN/data science learn/Project- USA shooting/Shooting_USA.csv')

###discover data

df[['latitude', 'longitude','type', 'year']].describe(include='all')
df.info()
df.columns
df.shape
df.head(5)


###Data cleaning

# type
# mass change to Mass
df['type'] = df['type'].replace('mass', 'Mass', regex=True)
df['type'].value_counts()


#longitude and latitde
# covert - to NaN
df['latitude'] = df['latitude'].replace('-', np.nan)
df['longitude'] = df['longitude'].replace('-', np.nan)

#datatype conversion
df['latitude'] = df['latitude'].astype('float')
df['longitude'] = df['latitude'].astype('float')
df.dtypes

# gender
df['gender'] = df['gender'].replace('Male', 'M' )
df['gender'] = df['gender'].replace('Female', 'F' )
df['gender'] = df['gender'].replace('Male & Female', 'Unknown')

# location- state and city
df['state'] = df['location'].apply(lambda x: x.split(',')[1])
df['city'] = df['location'].apply(lambda x: x.split(',')[0])

# race
df.race = df.race.astype('str').str.lower().str.strip()
df['race'] = df['race'].replace('-', 'unclear' , regex=True)


# age
df['age_of_shooter'] = df['age_of_shooter'].replace('-', 0 , regex=True).astype('int')
#print(df[df['age_of_shooter'].isna()].summary)

#mental health
df['prior_signs_mental_health_issues'] = df['prior_signs_mental_health_issues'].astype('str').str.lower().str.strip()
df['prior_signs_mental_health_issues'] = df['prior_signs_mental_health_issues'].replace(['-', 'tbd', 'unclear', 'unknown'], 'unknown' , regex=True)


# date column- 
df.date = pd.to_datetime(df['date']) #.dt.strftime('%Y-%m-%d')

# weapons_obtain
df.weapons_obtained_legally = df['weapons_obtained_legally'].apply(lambda x: 'yes' if 'yes' in x.lower() else 'no')

#location.1
df['social_area'] = df['location.1'].astype('str').str.strip().str.lower()
#df.drop(columns = ['location.1'], inplace= True)

#create a new column with all the news_scr
df['news_source'] = df.sources +df.sources_additional_age

#source of data
def func_scr(s):
    #multiple source
    r = list() 
    if s =='-':
        return list()
    
    while ";" in s:
        link = s.split(";")[0]
        web_page = link.split("/")[2]
        r.append(web_page.split(".")[-2])
        #print(s.split(";")[0])
        s= s.split(";")[1]
    if ";" not in s:
        r.append(s.split(";")[0].split("/")[2].split(".")[-2])
    return r
df['news_source'] = df.news_source.apply(lambda x: func_scr(x))

#drop column- 
df.drop(columns = ['sources', 'sources_additional_age'], inplace =True)

#find missing values
df.isna().sum()

# fill into lag and lat using different dataset
# not unique here
cities = pd.read_csv('C:/Users/AIMAN/data science learn/Project- USA shooting/uscities.csv')
cities.drop(columns= [ 'city_ascii', 'state_id', 'county_fips',
       'county_name', 'population', 'density', 'source',
       'military', 'incorporated', 'timezone', 'ranking', 'zips', 'id'],
            inplace= True)

cities['location'] = cities['city']+', ' + cities['state_name']

cities.drop_duplicates(inplace=True) 
cities.location.drop_duplicates(inplace=True) 

#merge dataset
df = pd.merge(df, cities, on='location',how='left')
df.drop(columns= ['latitude', 'longitude'], inplace=True)

#create columns

# date
df['month'] = df.date.dt.month_name().str.slice(stop=3)
df['weekday'] = df.date.dt.weekday



###Visualizations

# Get shooting for each month- barplot
monthly_shooting= df['month'].value_counts()

Month_order=['Jan', 'Feb', 'Mar', 'Apr', 'May', 
             'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
             'Nov', 'Dec']

plt.figure(figsize=(12,5))
sns.barplot(x=Month_order, y=monthly_shooting)
plt.title("Shooting over Month")
plt.xticks(rotation=45)
plt.ylabel("No. of shooting")
plt.xlabel("Months")
plt.show()

# Get shooting for each year- line chart
#x = pd.DataFrame(df['year'].value_counts().sort_values())
#x.index = x.index.sort_values()
x = (df[['year','case_name']].groupby('year').count().sort_values('year'))
plt.figure(figsize=(12,5))
plt.plot(x.index, x.case_name, marker='o')
plt.title("Shooting over years")
plt.xticks(rotation=45)
plt.ylabel("No. of shooting")
plt.xlabel("Years")
plt.show()

# race wise shooting rate
# x=pd.DataFrame(df['race'].value_counts())
x=df['race'].value_counts().reset_index()
plt.figure(figsize=(12,5))
plt.pie(x.race, labels=x['index'], autopct='%1.1f%%', startangle=140) # y then x
plt.title("Shooting vs Race")
plt.show()

# race wise shooting rate
x=pd.DataFrame(df['social_area'].value_counts())
plt.figure(figsize=(12,5))
plt.pie(x.social_area, labels=x.index, autopct= '%1.1f%%')
plt.title("Shooting vs social_area")
plt.axis('equal')
plt.show()

# geographical distribution
from mpl_toolkits.basemap import Basemap

# Count the occurrences of each city name
city_counts = df['location'].value_counts()



# Create a figure and Basemap
fig = plt.figure(figsize=(12, 8))
m = Basemap(projection='merc', llcrnrlat=-80, 
            urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, 
            resolution='c')

# Scatter plot the cities with colors based on counts
for location, count in city_counts.items():
    city_data = df[df['location'] == location]
    x, y = m(city_data['lng_y'].values[0], city_data['lat_y'].values[0])
    color = count / city_counts.max()  # Scale color by count
    plt.scatter(x, y, s=50, c=[color], cmap='YlOrRd', alpha=0.7)

# Customize the colorbar
plt.colorbar(label='City Count')

# Draw coastlines, country boundaries, etc.
m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(fill_color='lightblue')

plt.title('City Point Map')
plt.show()

df.sort_values(by='year', inplace= True)