#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
from collections import OrderedDict

from random import randint # For generating test data

CLIENT_FORMAT_FILE = "client_format.json"
DATABASE_FORMAT_FILE = "database_format.json"
DATABASE_COLLECTION = "telemetry"

cred = credentials.Certificate("ku-solar-car-b87af-firebase-adminsdk-ttwuy-0945c0ac44.json")
firebase_admin.initialize_app(cred, {"projectId": "ku-solar-car-b87af"})
db = firestore.client()

app = Flask(__name__)

# Determines what each tab/graph should display
with open(CLIENT_FORMAT_FILE) as file_handle:
	client_format = json.load(file_handle)

# Specifies information about each sensor in the database
with open(DATABASE_FORMAT_FILE) as file_handle:
	db_format = json.load(file_handle)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/realtime', methods=['GET'])
def realtime():
	return "NYI"
	#return render_template('realtime.html', data=data)
	
# TODO: Endpoint for AJAX requests to update data on realtime page
	
@app.route('/daily', methods=['GET'])
def daily():
	try:
		# Check if valid date was provided as GET parameter
		date = datetime.strptime(request.args.get('date', default=""), '%Y-%m-%d')
	except ValueError:
		# Default to today (at midnight) if not
		date = datetime.combine(datetime.today(), datetime.min.time())
	
	# Formatted date strings when rendering page and buttons to other dates
	date_str = date.strftime('%Y-%m-%d')
	prev_date_str = (date-timedelta(1)).strftime('%Y-%m-%d')
	next_date_str = (date+timedelta(1)).strftime('%Y-%m-%d')
	
	tab_list = client_format.keys()
	
	try:
		tab = request.args.get('tab')
		if not tab in client_format.keys(): raise ValueError()
	except ValueError:
		tab = next(iter(client_format))
	
	#print("==== " + date_str: tab + " ====" + "="*100)	
	
	graph_data = OrderedDict() # The data used in the render template (see format below)
	""" graph_data = {
			"Voltage": {"1579970374000": 423, "1579970379000": 419, ...},
			"Current": {"1579970374000": 46, "1579970379000": 48, ...},
		} """
	
	# Loop through every sensor the current tab should show a reading for
	for sensor_id in client_format[tab]["lines"]:
	
		# Find the info about the sensor
		sensor = next((item for item in db_format if item["id"] == sensor_id), None)
		# Ensure the sensor is in the database
		if sensor is not None and "name" in sensor:
			graph_data[sensor["name"]] = OrderedDict()
			#print("-- " + str(sensor["index"]) + ": " + sensor_id + " --")
			
			# Loop through all the sensor readings for the day being viewed
			db_data = db.collection(DATABASE_COLLECTION).document(date_str).collection(sensor["id"]).stream()
			try:
				readings = next(db_data).to_dict()["seconds"] # The map within the sensor's document
			except StopIteration:
				continue # Skip sensors not in database
			
			for time, reading in sorted({int(k) : v for k, v in readings.items()}.items()):					
				unix = int(date.timestamp() + int(time))*1000
				graph_data[sensor["name"]][unix] = reading
				#print(str(unix) + ": " + str(reading))
		
		
	#print("graph_data: " + json.dumps(graph_data))
	
	return render_template('daily.html', **locals())
	
@app.route('/longterm', methods=['GET'])
def longterm():
	return "NYI"
	
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
		
	TEST_SENSORS = {"battery_voltage": [300, 400], "battery_current": [200, 500], "bms_fault": [0, 1], "battery_level": [60, 70]};
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