function initMap() {
    var follow_car = true;

    // The location of Daytona
    var location = {lat: 29.187668, lng: -81.072786};

    // The map, centered at Daytona
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 15, center: location});

    image = 'car.png'; // TODO: Get image for car

    // The marker, positioned at Daytona
    var marker = new google.maps.Marker({position: location, map: map, icon: image});

    function move_car(lat, lng) {
        marker.setPosition(new google.maps.LatLng(lat, lng));

        if(follow_car === true) {
            map.panTo(new google.maps.LatLng(lat, lng));
        }
    }

    move_car(29.186839, -81.063373);

    var latRef = firebase.database().ref('lat');
    latRef.on('value', function(snapshot) {
        location.lat = snapshot.val();
        move_car(location.lat, location.lng);
    });

}