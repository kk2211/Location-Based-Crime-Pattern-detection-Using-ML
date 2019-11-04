import pandas as pd
import operator

def getLocations():
    df = pd.read_csv('news_data.csv')
    locations = []
    for i in df['location']:
        if i != 'aiims':
            s = i.split()
            loc = []
            for j in s:
                loc.append(j[0].upper() + j[1:])
            locations.append(' '.join(loc))
        else:
            locations.append(i.upper())
    locations = sorted(locations)
    return locations

def getData(loc_name, age):
    df = pd.read_csv('news_data.csv')
    df_new = df[df['location']==loc_name]
    headlines = list(df_new['headline'])[0].split('\t')
    dates = list(df_new['date'])[0].split('\t')
    crime_types = list(df_new['crime_type'])[0].split('\t')
    ages = list(df_new['age'])[0].split('\t')
    businessmans = list(df_new['businessman'])[0].split('\t')

    crime_count = len(headlines)
    no_businessman = businessmans.count('1')

    age_groups = [0, 22, 51, 101]

    min_age = 0
    max_age = 100
    for i in range(1):
        if age>=age_groups[i] and age<age_groups[i+1]:
            min_age = age_groups[i]
            max_age = age_groups[i+1]

    crimes_age = 0
    lst = []
    for i in range(len(ages)):
        if int(ages[i])>=min_age and int(ages[i])<=max_age:
            crimes_age+=1
            lst.append(crime_types[i])

    if len(lst)!=0:
        s = str(max(set(lst), key = lst.count))
        s = s[0].upper() + s[1:]
    else:
        s = -1


    crimes = {'burglary':crime_types.count('burglary'),
              'robbery':crime_types.count('robbery'),
              'murder':crime_types.count('murder'),
              'kidnapping':crime_types.count('kidnapping'),
              'rape':crime_types.count('rape')}
    age_crimes = {'0-21':0,
                  '22-50':0,
                  '50+':0,
                  'NA':0}

    for k in ages:
        i = int(k)
        if i>=0 and i<=21:
            age_crimes['0-21']+=1
        elif i>21 and i<=50:
            age_crimes['22-50']+=1
        elif i>50:
            age_crimes['50+']+=1
        else:
            age_crimes['NA']+=1

    x = str(sorted(crimes.items(), key=operator.itemgetter(1))[::-1][0][0])
    most_occ_crime = x[0].upper() + x[1:]
    return [dates, headlines, crime_types], crime_count, crimes_age, no_businessman, crimes, age_crimes, most_occ_crime, s

def safetyIndex(loc):
    si = 0
    df = pd.read_csv('news_data.csv')
    for i in range(len(df)):
        if df['location'].iloc[i]==loc:
            si = df['percentile'].iloc[i]
            break

    return si