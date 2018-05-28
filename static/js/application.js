
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('livematch', function(msg) {
        console.log("Received number" + msg.score_team_1);
        console.log("Received number 2" + msg.score_team_2);
        //maintain a list of ten numbers
        $('#score_team_1').html(msg.score_team_1.toString());
        $('#score_team_2').html(msg.score_team_2.toString());
    });

});
