#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
from collections import OrderedDict

CLIENT_FORMAT_FILE = "client_format.json"
DATABASE_FORMAT_FILE = "database_format.json"
DATABASE_COLLECTION = "telemetry"

cred = credentials.Certificate("ku-solar-car-b87af-firebase-adminsdk-ttwuy-0945c0ac44.json")
firebase_admin.initialize_app(cred, {"projectId": "ku-solar-car-b87af"})
db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/realtime', methods=['GET'])
def realtime():
	return "NYI"
	#return render_template('realtime.html', data=data)
	
# TODO: Endpoint for AJAX requests to update above data on realtime page
	
@app.route('/daily', methods=['GET'])
def daily():
	date_raw = request.args.get('date', default="")
	try:
		# Verify valid date was provided
		date = datetime.strptime(date_raw, '%Y-%m-%d')
	except ValueError:
		# Default to today (at midnight)
		date = datetime.combine(datetime.today(), datetime.min.time())
		
	# Formatted date strings when rendering page and buttons to other dates
	date_str = date.strftime('%Y-%m-%d')
	prev_date_str = (date-timedelta(1)).strftime('%Y-%m-%d')
	next_date_str = (date+timedelta(1)).strftime('%Y-%m-%d')
	
	with open(CLIENT_FORMAT_FILE) as file_handle:
		tab_format = json.load(file_handle)
		
	with open(DATABASE_FORMAT_FILE) as file_handle:
		db_format = json.load(file_handle)
		
	# Get the data from the database corresponding to the current date
	# >= and <= are used instead of == due to time zone issues
	db_data = db.collection(DATABASE_COLLECTION).where("date", ">=", date).where("date", "<=", date+timedelta(1)).stream()
	try:
		readings = next(db_data).to_dict()["telemetry"]
	except StopIteration:
		readings = []
		#return "No data for " + date_str
	
	# Tabs array represents each different graph tab visible on the client side
	tabs = []
	for tab in tab_format:
		tabs.append(tab)
		print("===== TAB: " + tab + " =====")
		# Loop through every sensor the current tab should show a reading for
		for sensor_id in tab_format[tab]["lines"]:
			# Find the info about the sensor
			sensor = next((item for item in db_format if item["id"] == sensor_id), None)
			# Ensure the sensor is in the database
			if sensor is not None and "index" in sensor:
				print("-- " + str(sensor["index"]) + ": " + sensor_id + " --")
				# Loop through all the sensor readings for the day being viewed
				for reading in readings:
					print(reading + ": " + str(readings[reading][sensor["index"]]))
			
		
	
	return "Testing" # ========================================================
	
	
	graph_data = {} # The data from the database that will be plotted on each graph
	graph_labels = {} # The keys for each of the types of data per graph
	
	for tab in tabs:
		graph_data[tab] = OrderedDict()
		init_labels = False
		
		tab_data = db.collection(tab).order_by("time").stream()
		for entry in tab_data:
			dict = entry.to_dict()
			print('{} => {}'.format(entry.id, dict))
			
			# Create graph_labels (each piece of data that will be a line on the graph)
			if init_labels == False:
				graph_labels[tab] = dict.keys()
				init_labels = True
			
			# Skip entries without time (should not exist)
			if not "time" in dict: continue
			
			# Convert time format from database to UNIX timestamp, then remove from dict
			timestamp = int(dict["time"].timestamp())*1000
			del dict["time"]
			
			dict.pop('location', None) # TEMPORARY
			
			graph_data[tab][timestamp] = dict
			
		for k,v in graph_data[tab].items():
			print("TEST: " + str(k))
	
	print("GRAPH LABELS: " + str(graph_labels))
	
	# list(data.keys()).sort()
		
	return render_template('daily.html', **locals())
	
@app.route('/longterm', methods=['GET'])
def longterm():
	return "NYI"
	
if __name__ == '__main__':
    app.run()