#!/usr/bin/env python3

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
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
	
	return render_template('index.html', data=data)
	
if __name__ == '__main__':
    app.run()