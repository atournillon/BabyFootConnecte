
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('livematch', function(msg) {
        console.log("Received number" + msg.score_b);
        console.log("Received number 2" + msg.score_r);
        //maintain a list of ten numbers
        $('#score_b').html(msg.score_b.toString());
        $('#score_r').html(msg.score_r.toString());
    });

});
