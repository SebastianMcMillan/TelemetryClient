window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};


function newDateString(ms) {
	let timestmp = Date.now()+ms;
	let mom = moment(timestmp);
    return mom.toDate();
}


var color = Chart.helpers.color;
var config = {
    type: 'bar',
    data: {
        datasets: [{
            backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
            borderColor: window.chartColors.blue,
            fill: false,
            data: []
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
        },
		legend: {
        	display: false,
		},
        scales: {
            xAxes: [{
                type: 'time',
                display: true,
				offset: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Date'
                },
                ticks: {
					maxRotation: 0,
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'value'
                },
				ticks: {
                	min: -1,
					max: 1,
				}
            }]
        }
    }
};

let new_data_queue = [];
let time_queue = [];

window.onload = function() {
    var ctx = document.getElementById('canvas').getContext('2d');
    window.myLine = new Chart(ctx, config);

    setInterval(checkForData, 1000);
    setInterval(updateChart, 1000);
};


/*
Adds data to new_data_queue
 */
function checkForData() {
    const http = new XMLHttpRequest();
    const url = "http://127.0.0.1:5000/realtime/give-bool";
    http.open("GET", url);
    http.send();

    http.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let bool = parseInt(http.responseText);
            if (bool) {
            	new_data_queue.push(1);
			} else {
            	new_data_queue.push(-1);
			}

			time_queue.push(newDateString(0));
        }
    };
}


/*
Updates chart with values from new_data_queue, then deletes values from new_data_queue
 */
function updateChart() {
	let data = config.data.datasets[0].data;
	for (let i=0; i < new_data_queue.length; i++) {
		if(data.length > 5) {
			data.splice(0, 1);
		}
		data.push({
			x: time_queue[i],
			y: new_data_queue[i]
		});
		time_queue.splice(i, 1);
		new_data_queue.splice(i, 1);
		window.myLine.update();
    }
	updateHead(data[data.length-1].y)
}


function updateHead(new_val) {
	let header = document.getElementById("head");
	// header.innerText = "Value: " + new_val;
}
