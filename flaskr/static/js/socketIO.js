function socketIOinit() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log('Websocket connected!');
    });
    
    //start daemon to read temperature
    socket.emit('handleDaemon', {name: '1', action: 'START'});

    socket.on('daemonProcess', function(data) {
        var jObj = JSON.parse(data);
        var requestSid = jObj.requestSid; 
        var dateTime = jObj._EnvironmentData__dateTime;
        var temperature = jObj._EnvironmentData__temperature;
        var humidity = jObj._EnvironmentData__humidity;
        var sensorSimulation = jObj._EnvironmentData__sensorSimulation;
        var temperatureReached = jObj._EnvironmentData__temperatureReached;
        console.log(jObj);
        if (sensorSimulation) {
            document.getElementById('sensorSimulation').style.display = 'block';
        } else {
            document.getElementById('sensorSimulation').style.display ='none';
        }
        if (!temperatureReached) {
            document.getElementById('flameOn').style.display = 'none';
            document.getElementById('flameOff').style.display = 'block';
        } else {
            document.getElementById('flameOn').style.display = 'block';
            document.getElementById('flameOff').style.display = 'none';
        }
        document.getElementById('temperature').innerHTML = temperature;
        document.getElementById('humidity').innerHTML = humidity;
    });
}