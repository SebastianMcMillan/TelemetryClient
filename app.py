#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
#cred = credentials.ApplicationDefault()
cred = credentials.Certificate("ku-solar-car-b87af-firebase-adminsdk-ttwuy-0945c0ac44.json")
firebase_admin.initialize_app(cred, {
  "projectId": "ku-solar-car-b87af",
})

db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/realtime', methods=['GET'])
def realtime():
	# TODO: Get this from database
	data = {
		"BMS": {
			"Voltage": [" V", 423.5],
			"Current": [" A", 45.3],
			"Charge": ["%", 83],
			"Temperature": ["°C", 38.0],
		},
		"Motor": {
			"Power": [" W", 952.1],
			"Speed": [" mph", 40.3],
			"Temperature": ["°C", 47.3],
		},
		"GPS": {
			"Timestamp": ["", "2019-10-28 18:41:37"],
			"Speed": [" mph", 38.7],
			"Location": ["", '38.9600781,-95.2468986'], #<a href="https://www.google.com/maps/@38.9600781,-95.2468986,14z" target="_blank">
			"Altitude": [" ft", 865],
			"Number of satellites": ["", 5],
		},
	}
	
	return render_template('realtime.html', data=data)
	
# TODO: Endpoint for AJAX requests to update above data
	
@app.route('/daily', methods=['GET'])
def daily():
	date_raw = request.args.get('date', default="")
	try:
		# Verify valid date was provided
		date = datetime.strptime(date_raw, '%Y-%m-%d')
	except ValueError:
		# Default to today
		date = datetime.today()
		
	date_str = date.strftime('%Y-%m-%d')
	prev_date_str = (date-timedelta(1)).strftime('%Y-%m-%d')
	next_date_str = (date+timedelta(1)).strftime('%Y-%m-%d')
	
	TABS = ["battery", "motor", "solar", "speed"]
	
	graphs = {}
	for tab in TABS:
		graphs[tab] = []
		tab_data = db.collection(tab).stream()
		for entry in tab_data:
			print('{} => {}'.format(entry.id, entry.to_dict()))
			graphs[tab].append(entry.to_dict()) 
			# TODO: Switch to below so keys are timestamps, change [] to {} above, remove time from entry.to_dict() below
			# Need database to have time entry for all data to do this
			# graphs[tab][to_milliseconds(entry.time)] = entry.to_dict()
	
	"""graphs = {
		"Battery": {},
		"Solar": {},
		"Motor": {},
		"Speed": {},
		"Temps": {},
		"Location": {} # TODO: Handle location separately (Google maps)
	}"""
	
	return render_template('daily.html', graphs=graphs, date_str=date_str, prev_date_str=prev_date_str, next_date_str=next_date_str)
	
@app.route('/longterm', methods=['GET'])
def longterm():
	return "NYI"
	
if __name__ == '__main__':
    app.run()