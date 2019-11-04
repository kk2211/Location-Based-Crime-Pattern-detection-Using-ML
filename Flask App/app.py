from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for, flash, sessions, session, get_flashed_messages
import pandas as pd


from get_details import getLocations, getData, safetyIndex
from update_news import updateNews
from get_safe_locations import getSafeLocations

app = Flask(__name__)
app.secret_key = "abc"

@app.route('/')
def splash():
    return render_template('splash.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    # updateNews()
    locations = getLocations()
    if request.method=='POST':
        session['age'] = request.form['age']
        session['location'] = request.form['location']
        session['gender'] = request.form['gender']
        session['businessman'] = request.form['businessman']
        return redirect(url_for('crimeDetails'))
    return render_template('index.html', locations = locations)


@app.route('/crime-details', methods=['GET', 'POST'])
def crimeDetails():
    age = session['age']
    location = session['location']
    gender = session['gender']
    businessman = session['businessman']



    if request.method=="POST":
        if request.form['distance'] == '2.5km':
            session['distance'] = 2.5
        elif request.form['distance'] == '5km':
            session['distance'] = 5
        elif request.form['distance'] == '10km':
            session['distance'] = 10

        # print(';svfsdv')
        # session['distance'] = request.form['distance']
        return redirect(url_for('safeAreas'))

    news, crime_count, crime_ages, no_businessman, crimes, age_crimes, most_occ_crime, s = getData(location.lower(), int(age))
    si = safetyIndex(location.lower())
    print(si)
    return render_template('crime-details.html', location=location, news=news, crime_count=crime_count, crime_ages=crime_ages, no_businessman=no_businessman, businessman=businessman, crimes=crimes, age_crimes=age_crimes, most_occ_crime=most_occ_crime, s=s, si=si)


@app.route('/safe-areas', methods=['GET', 'POST'])
def safeAreas():
    src_loc = session['location']
    dist = session['distance']
    safe_areas_lst, crime_area = getSafeLocations(src_loc.lower(), dist)

    return render_template('safe-areas.html', safe_areas_lst=safe_areas_lst, crime_area=crime_area, l=len(safe_areas_lst), src_loc=src_loc)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
