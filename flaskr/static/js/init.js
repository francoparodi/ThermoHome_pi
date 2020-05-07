function initOnLoad() {
    showDigitalClock(); 
    socketIOinit(); 
}

function showDigitalClock() {
    var date =  new Date().toLocaleString();
    document.getElementById("digitalClock").innerHTML = date;
    setTimeout(showDigitalClock, 1000);
}

function createSlider(id, idInput) {
    var slider1 = document.getElementById(id);
    var startValue = document.getElementById(idInput);
    noUiSlider.create(slider1, {
        start: startValue.value,
        connect: true,
        step: 1,
        range: {
            'min': 0,
            'max': 1800
        }
    });

    slider1.noUiSlider.on('update', function (values, handle) {    
        var inputValue = document.getElementById('readFromSensorIntervalSliderValue');
        inputValue.value = values[handle];
        var labelValue = document.getElementById('sensorIntervalSliderLabel');
        labelValue.innerHTML = "Read from sensor every " + inputValue.value + "s."
    });
}
