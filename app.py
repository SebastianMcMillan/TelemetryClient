#!/usr/bin/env python3

import json
from collections import OrderedDict
from datetime import datetime, timedelta
from random import randint  # For generating test data

import firebase_admin
import numpy as np  # For downsampling
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, render_template, request

from google_maps_key import key

MAX_POINTS = 500  # Min/max downsample data to this amount if larger

CLIENT_FORMAT_FILE = "client_format.json"
DATABASE_FORMAT_FILE = "database_format.json"
DATABASE_COLLECTION = "telemetry"

cred = credentials.Certificate("ku-solar-car-b87af-firebase-adminsdk-ttwuy-0945c0ac44.json")
firebase_admin.initialize_app(cred, {"projectId": "ku-solar-car-b87af"})
db = firestore.client()

app = Flask(__name__)

NAV_LIST = ["Realtime", "Daily", "Longterm"]



# Determines what each tab/graph should display
with open(CLIENT_FORMAT_FILE) as file_handle:
    client_format = json.load(file_handle)

# Specifies information about each sensor in the database
with open(DATABASE_FORMAT_FILE) as file_handle:
    db_format = json.load(file_handle)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# TODO: Javascript
@app.route('/Realtime', methods=['GET'])
def realtime():
    nav_list = NAV_LIST
    nav = "Realtime"
    return render_template('realtime.html', **locals())


@app.route('/Daily', methods=['GET'])
def daily():
    nav_list = NAV_LIST
    nav = "Daily"
    # Check if valid date was provided as GET parameter, default to today (at midnight) if not
    try:
        date = datetime.strptime(request.args.get('date', default=""), '%Y-%m-%d')
    except ValueError:
        date = datetime.combine(datetime.today(), datetime.min.time())

    # Formatted date strings when rendering page and buttons to other dates
    date_str = date.strftime('%Y-%m-%d')
    prev_date_str = (date-timedelta(days=1)).strftime('%Y-%m-%d')
    next_date_str = (date+timedelta(days=1)).strftime('%Y-%m-%d')

    tab_list = client_format.keys()

    # Check if valid tab was provided as GET parameter, default to default to first tab if not
    try:
        tab = request.args.get('tab')
        if not tab in client_format.keys(): raise ValueError()
    except ValueError:
        tab = next(iter(client_format))

    graph_data = OrderedDict()  # The data used in the render template (see format below)

    if tab == "Location":  # Location tab uses separate template to display map
        # URL to initialize Google Maps API, to be injected into HTML. Key: value is from local google_maps_key.py file.
        maps_url = key

        # Check if valid times were provided as GET parameter, default to all day if not
        try:
            # Times are represented by seconds from midnight
            starttime = int(request.args.get('starttime', default=''))
            endtime = int(request.args.get('endtime', default=''))
        except ValueError:
            starttime = 0
            endtime = 86400

        # Get list of latitudes. lat_gen is a generator of document snapshots, but will only yield one snapshot for us
        # given the firebase setup.
        lat_gen = db.collection(DATABASE_COLLECTION).document(date_str).collection('gps_lat').stream()

        # Avoid a server error if there's no data for the day (lat_gen yields no values)
        try:
            lat_reading_dict = next(lat_gen).to_dict()["seconds"]  # dict format: {'second': reading}, ex. {'10': 334}
        except StopIteration:
            location_pairs = None
            return render_template('daily_location.html', **locals())

        lat_reading_list = \
            sorted({int(k): v for k, v in lat_reading_dict.items() if starttime <= int(k) <= endtime}.items())
        sec_list, lat_list = zip(*lat_reading_list)

        # Get list of longitudes in the same manner
        lon_gen = db.collection(DATABASE_COLLECTION).document(date_str).collection('gps_lon').stream()

        try:
            lon_reading_dict = next(lon_gen).to_dict()["seconds"]
        except StopIteration:
            location_pairs = None
            return render_template('daily_location.html', **locals())

        lon_reading_list = \
            sorted({int(k): v for k, v in lon_reading_dict.items() if starttime <= int(k) <= endtime}.items())
        sec_list, lon_list = zip(*lon_reading_list)

        location_pairs = zip(lat_list, lon_list)  # [(lat0, lon0), (lat1, lon1), ...]

        return render_template('daily_location.html', **locals())
    else:
        # Loop through every sensor the current tab should show a reading for
        for sensor_id in client_format[tab]["lines"]:

            # Find the info about the sensor
            sensor = db_format[sensor_id]
            # Ensure the sensor is in the database
            if sensor is not None and "name" in sensor:
                graph_data[sensor["name"]] = OrderedDict()

                # Loop through all the sensor readings for the day being viewed
                db_data = db.collection(DATABASE_COLLECTION).document(date_str).collection(sensor_id).stream()
                try:
                   readings = next(db_data).to_dict()["seconds"] # The map within the sensor's document
                except StopIteration:
                    continue # Skip sensors not in database

                # Convert keys from strings to ints and sort (conversion required for sort to be correct)
                sorted_readings = sorted({int(k) : v for k, v in readings.items()}.items())

                # Convert the sorted list of tuples into two separate lists using zip
                times, readings = zip(*sorted_readings)

                # Downsample data if needed
                if len(readings) > MAX_POINTS:
                    times, readings = avg_downsample(np.array(times), np.array(readings), MAX_POINTS)

                for time, reading in zip(times, readings):
                    unix = int(date.timestamp() + time)*1000
                    graph_data[sensor["name"]][unix] = reading

        return render_template('daily.html', **locals())


# https://stackoverflow.com/questions/10847660/subsampling-averaging-over-a-numpy-array
def avg_downsample(x, y, num_bins):
    pts_per_bin = x.size // num_bins
    end = pts_per_bin * int(len(y)/pts_per_bin)
    x_avgs = np.mean(x[:end].reshape(-1, pts_per_bin), 1)
    y_avgs = np.mean(y[:end].reshape(-1, pts_per_bin), 1)
    y_avgs = np.round(y_avgs, 2)
    return x_avgs, y_avgs


# A different downsampling method. This is currently not being used, but left as an option for the future
# https://stackoverflow.com/questions/54449631/improve-min-max-downsampling
def min_max_downsample(x, y, num_bins):
    pts_per_bin = x.size // num_bins

    x_view = x[:pts_per_bin*num_bins].reshape(num_bins, pts_per_bin)
    y_view = y[:pts_per_bin*num_bins].reshape(num_bins, pts_per_bin)
    i_min = np.argmin(y_view, axis=1)
    i_max = np.argmax(y_view, axis=1)

    r_index = np.repeat(np.arange(num_bins), 2)
    c_index = np.sort(np.stack((i_min, i_max), axis=1)).ravel()

    return x_view[r_index, c_index], y_view[r_index, c_index]


@app.route('/Longterm', methods=['GET'])
def longterm():
    nav_list = NAV_LIST
    nav = "Longterm"
    return render_template('longterm.html', **locals())


# Throwaway test endpoint
@app.route('/generate-dummy-data', methods=['GET'])
def dummy():
    try:
        # Check if valid date was provided as GET parameter
        date = datetime.strptime(request.args.get('date', default=""), '%Y-%m-%d')
    except ValueError:
        return "Invalid or missing date GET parameter"

    # Ensure day does not have any (possibly real) data already (the exception is the goal)
    date_str = date.strftime('%Y-%m-%d')
    db_data = db.collection(DATABASE_COLLECTION).where("date", "==", date_str).stream()
    try:
        readings = next(db_data)
        return "Date already has data"
    except StopIteration: # This means its safe to generate data (without overwriting)
        pass

    TEST_SENSORS = \
        {"battery_voltage": [300, 400], "battery_current": [200, 500], "bms_fault": [0, 1], "battery_level": [60, 70]}
    date_doc = db.collection(DATABASE_COLLECTION).document(date_str)

    for sensor, rand_range in TEST_SENSORS.items():
        dummy_data = {"seconds": {}}
        for i in range(0, 86400, 5):
            dummy_data["seconds"][str(i)] = randint(rand_range[0], rand_range[1])
        date_doc.collection(sensor).document("0").set(dummy_data, merge=True)
        #print(dummy_data)

    return "OK"


if __name__ == '__main__':
    app.run()
