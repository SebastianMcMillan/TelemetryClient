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
	
	#print("==== " + date_str + " ====" + "="*100)
	
	
	# Get the data from the database corresponding to the correct date
	db_data = db.collection(DATABASE_COLLECTION).where("date", "==", date_str).stream()
	try:
		readings = next(db_data).to_dict()["telemetry"] # The map within the read document
		readings = OrderedDict(sorted(readings.items())) # Sort the map
		#print("readings: " + str(readings))
	except StopIteration:
		readings = {} # No document for day requested
	
	
	graph_data = OrderedDict() # The data rearranged for usage in the render template (see format below)
	""" graph_data {
			"Battery": {
				"Voltage": {"1579970374000": 423, "1579970379000": 419, ...},
				"Current": {"1579970374000": 46, "1579970379000": 48, ...},
				...
			}, "Solar": ...
		} """
	
	
	# Tabs array represents each different graph tab the user can look at
	tabs = []
	for tab, tab_data in client_format.items():
		tabs.append(tab)
		graph_data[tab] = OrderedDict()
		#print("===== TAB: " + tab + " =====")
		
		# Loop through every sensor the current tab should show a reading for
		for sensor_id in tab_data["lines"]:
		
			# Find the info about the sensor
			sensor = next((item for item in db_format if item["id"] == sensor_id), None)
			# Ensure the sensor is in the database
			if sensor is not None and "index" in sensor:
				graph_data[tab][sensor["name"]] = OrderedDict()
				#print("-- " + str(sensor["index"]) + ": " + sensor_id + " --")
				
				# Loop through all the sensor readings for the day being viewed
				for time, reading in readings.items():					
					unix = int(date.timestamp() + int(time))*1000 # TODO: Timezone incorrect
					graph_data[tab][sensor["name"]][unix] = reading[sensor["index"]]
					#print(str(unix) + ": " + str(reading[sensor["index"]]))
			
		
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
	except StopIteration: # This means we're good to generate data
		dummy_data = {
			"date": date_str,
			"telemetry": {
			}
		}
		
		#for i in range(randint(20000, 40000), randint(70000, 80000), 5):
		#for i in range(randint(55000, 60000), randint(65000, 70000), 5):
		for i in range(20000, 40000, 5):
			dummy_data["telemetry"][str(i)] = [
				randint(300, 400),
				randint(200, 500),
				randint(0, 1)
			]
			
		#db.collection(DATABASE_COLLECTION).document("ID GOES HERE").set(dummy_data, merge=True)
		db.collection(DATABASE_COLLECTION).add(dummy_data)
		
	return "OK"
	
if __name__ == '__main__':
    app.run()