var map = null;

var firebaseConfig = {
                apiKey: "AIzaSyAgnNvoWACZjxgey_Dd54zlyRN6X65SSug",
                authDomain: "ku-solar-car-b87af.firebaseapp.com",
                databaseURL: "https://ku-solar-car-b87af.firebaseio.com",
                projectId: "ku-solar-car-b87af",
                storageBucket: "ku-solar-car-b87af.appspot.com",
                messagingSenderId: "840177102905",
                appId: "1:840177102905:web:c475831bc192c5d4f09de8",
                measurementId: "G-GWKJM2LZWE"
            };

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
var database = firebase.database();


function initMap() {
    // The location of Daytona
    var location = {lat: 29.187668, lng: -81.072786};

    // The map, centered at Daytona
    map = new google.maps.Map(document.getElementById('map'), {zoom: 15, center: location});

    var image = 'images/car.png'; // TODO: Add image for car

    // The marker, positioned at Daytona
    var marker = new google.maps.Marker({position: location, map: map});

    function move_car(lat, lng) {
        marker.setPosition(new google.maps.LatLng(lat, lng));
    }

    move_car(29.186839, -81.063373);
}

function update_map() {
    // TODO: Get values from date selectors


    // Get values from time selectors
    var start_time = document.getElementById("start-time").value;
    var end_time = document.getElementById("end-time").value;

    start_time = start_time * 3600; // convert hours into seconds after t=0
    end_time = end_time * 3600;

    console.log(start_time);
    console.log(end_time);

    // TODO: convert time values into seconds

    // TODO: retrieve long and lat pairs from fb using time/date

    // TODO: put markers on all long and lat pairs

    // TODO: draw lines between consecutive markers
}
