function socketIOinit() {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log('websocket connected');
    });
    
    //start daemon
    socket.emit('handleDaemon', {name: '1', action: 'START'});

    //socket emit
    socket.on('daemonProcess', function(data) {
        var jObj = JSON.parse(data);
        var dateTime = jObj._EnvironmentData__dateTime;
        var temperature = jObj._EnvironmentData__temperature;
        var humidity = jObj._EnvironmentData__humidity;
        var sensorSimulation = jObj._EnvironmentData__sensorSimulation;
        var flameOn = jObj._EnvironmentData__flameOn;
        if (sensorSimulation) {
            document.getElementById('sensorSimulation').style.display = 'block';
        } else {
            document.getElementById('sensorSimulation').style.display ='none';
        }
        if (flameOn) {
            document.getElementById('flameOn').style.display = 'block';
            document.getElementById('flameOff').style.display = 'none';
        } else {
            document.getElementById('flameOn').style.display = 'none';
            document.getElementById('flameOff').style.display = 'block';
        }
        document.getElementById('temperature').innerHTML = temperature;
        document.getElementById('humidity').innerHTML = humidity;
    });
}