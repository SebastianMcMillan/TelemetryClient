// set initial values for time dropdowns
function set_select(select, value) {
    let options = select.options;
    for (let i = 0; i < options.length; i++) {
        if (options[i].value === value) {
            options[i].selected = true;
            break;
        }
    }
}
set_select(document.getElementById("start-time"), starttime.toString());
set_select(document.getElementById("end-time"), endtime.toString());

// verify dropdown values
function on_select_change() {
    let start = Number(document.getElementById("start-time").value);
    let end = Number(document.getElementById("end-time").value);

    if (start < end) {
        document.getElementById("time-form").submit()
    } else {
        alert("Selected start time must be prior to selected end time");
    }

}
// map
let map = null;

function draw_map() {
    let location = {lat: 0, lng: 0};

    // initialize the map
    map = new google.maps.Map(document.getElementById('map'), {zoom: 15, center: location});

    let image = 'images/car.png'; // TODO: Add image for car

    // The marker
    let marker = new google.maps.Marker({position: location, map: map});
    marker.setPosition(location);

    // TODO:
}
