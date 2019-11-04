import pandas as pd

def getSafeLocations(src_loc, dist):
    safe_area = []
    crime_area = []
    df = pd.read_csv('location_distance.csv')
    df = df[df['source']==src_loc]
    df = df[df['destination_crime_count'] != 0]
    src_crime_count = list(df['source_crime_count'])[0]

    for i in range(len(df)):
        dest_crime_count = df['destination_crime_count'].iloc[i]
        if src_crime_count > dest_crime_count:
            dist_1 = int(df['distance'].iloc[i])
            dest_area = str(df['destination'].iloc[i])
            if dist_1 <= dist:
                if dest_area=='aiims':
                    s = dest_area.upper()
                else:
                    dest_area = dest_area.split()
                    s = ""
                    for j in dest_area:
                        s = s + j[0].upper() + j[1:] + " "
                safe_area.append(s)
                dest_crime_percentile = df['dest_percentile'].iloc[i]
                crime_area.append(int(dest_crime_percentile))
    return safe_area, crime_area
