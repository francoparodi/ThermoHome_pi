var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
var language = navigator.languages[0];

function initOnLoad() {
    initDays();
    showDigitalClock(); 
    socketIOinit(); 
}

function initDays() {
    console.log(language);
    var date = new Date();
    for(day=1; day<8; day++){
        var dateToLocaleString = date.toLocaleString(language, options);    
        document.getElementById("day"+day).innerHTML = dateToLocaleString.substring(0,3).toUpperCase();
        date.setDate(date.getDate()+1);
    }
}

function showDigitalClock() {
    var date = new Date().toLocaleString(language, options);
    document.getElementById("digitalClock").innerHTML = date;
    setTimeout(showDigitalClock, 1000);
}

function createTimeSlider(sliderId, sliderValueId) {
    var range = {
        'min': [ 0 ],
        'max': [ 24 ]
    };
    var slider = document.getElementById(sliderId);
    var sliderValue = document.getElementById(sliderValueId);
    sliderValues = sliderValue.value.split(',');
    console.log(sliderValues);
        noUiSlider.create(slider, {
            start: sliderValues,
            connect: [false, true, false, true, false, true, false],
            range: range,
            tooltips: true,
            orientation: 'vertical',
            direction: 'rtl',
            step: 0.5,
            pips: {
                mode: 'values',
                values: [ 0.0,  0.5,  1.0,  1.5,  2.0,  2.5,  3.0,  3.5,  4.0,  4.5,  5.0,  5.5,  6.0,  
                          6.5,  7.0,  7.5,  8.0,  8.5,  9.0,  9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 
                         13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 
                         19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0],
                stepped: false
            },
            format: {
                // 'to' Receives a number.
                to: function (value) {
                    var strValue = String(value).split(".");
                    var hh = strValue[0];
                    var mm = "00";
                    if (strValue.length > 1) {
                        if (strValue[1].startsWith("5")){
                            mm = "30";
                        }
                    } 
                    return hh + ":" + mm;
                },
                // 'from' the formatted value.
                // Receives a string, should return a number.
                from: function (value) {
                    return Number(value.replace(":3", ".5"));
                }
            }
    });

    slider.noUiSlider.on('update', function (values, handle) {
        for (i=0; i<6; i++) {
            values[i] = formattedStringToTime(values[i]);
        }
        sliderValue.value = values;
    });
}

function timeToFormattedString(t){

}

function formattedStringToTime(s) {
    var strValue = String(s).split(":");
    var hh = strValue[0];
    var mm = "0";
    if (strValue.length > 1) {
        if (strValue[1].startsWith("3")){
            mm = "5";
        }
    } 
    return hh + "." + mm;
}

