window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};


let color = Chart.helpers.color;

// Don't make graphs for the data with these JSON keys.
IGNORED_KEYS = ["gps_time",
                "gps_lat",
                "gps_lon",
                "gps_velocity_east",
                "gps_velocity_north",
                "gps_velocity_up"];

// First, remove from the page charts we don't want, according to the keys above.
let card_containers = document.querySelectorAll(".card-container");
for(let i=0; i < card_containers.length-1; i++) {
    let con = card_containers[i];
    let con_id = con.id.split("-")[1];

    if (IGNORED_KEYS.includes(con_id)) {
        card_containers[i].parentNode.removeChild(con);
    }
}


// Canvases hold contexts. Charts are created by passing a context and a config dict.
let canvases = Array.from(document.getElementsByClassName("can"));
let contexts = canvases.map(x => {
    return x.getContext('2d')
});
let charts = contexts.map(x => new Chart(x, {
    type: 'line',
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
                    beginAtZero: true,
                    min: 0,
                    suggestedMax: 10
                }
            }]
        }
    }
}));

setInterval(checkForData, 2000);


/*
Requests new data and calls updateChart() with it.
 */
function checkForData() {
    const http = new XMLHttpRequest();
    const url = "/realtime/data1";
    http.open("GET", url);
    http.send();

    http.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let data = JSON.parse(http.responseText);
            for (let key in data) {
                for(let i = 0; i < charts.length; i++) {
                    let chart = charts[i];
                    let parsed_id = chart.canvas.id.split("-")[1];
                    if(parsed_id === key) {
                        updateChart(chart, [1000*parseInt(data["gps_time"])], [parseInt(data[key])]);
                    }
                }
            }
        }
    };
}


/*
Updates chart with values with paired values from time_queue, new_data_queue
 */
function updateChart(chart, time_queue, new_data_queue) {
	let data = chart.config.data.datasets[0].data;
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
		chart.update();
    }
	updateHead(chart)
}


/*
Update text at card head with the latest received value.
Update head background color to red if the value is dangerous.
Called from updateChart().
 */
function updateHead(chart) {
    let latest_val = chart.config.data.datasets[0].data[chart.config.data.datasets[0].data.length-1].y;
    let data_key = chart.canvas.id.split("-")[1];
    let head_key = "head-" + data_key;
    let header = document.getElementById(head_key);
    header.innerText = latest_val;

    let card_header = header.parentNode;

	if(latest_val > db_format[data_key]["safe_max"] || latest_val < db_format[data_key]["safe_min"]) {
	    if(!card_header.classList.contains("bg-danger")) {
	        card_header.classList.add("bg-danger");
            card_header.classList.add("text-white");
        }
    } else {
	    if(card_header.classList.contains("bg-danger")) {
	        card_header.classList.remove("bg-danger");
            card_header.classList.remove("text-white");
        }
    }
}
