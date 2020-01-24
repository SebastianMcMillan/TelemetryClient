#!/usr/bin/env python3

from flask import Flask, render_template, request
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from collections import OrderedDict

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
		# Default to today
		date = datetime.today()
		
	date_str = date.strftime('%Y-%m-%d')
	prev_date_str = (date-timedelta(1)).strftime('%Y-%m-%d')
	next_date_str = (date+timedelta(1)).strftime('%Y-%m-%d')
	
	TABS = ["battery", "motor", "solar", "speed"]
	
	graph_data = {} # The data from the database that will be plotted on each graph
	graph_labels = {} # The keys for each of the types of data per graph
	
	for tab in TABS:
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