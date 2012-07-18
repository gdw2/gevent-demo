$(function() {
    var ws = new WebSocket("ws://localhost:9999/test");
    var $placeholder = $('#placeholder');
    var datalen = 100;
    var plot = null;
    var series = {
        label: "Value",
        lines: { 
            show: true,
            fill: true,
            shadowSize: 25
        },
        points: {
            show:true
        },
        data: []
    };
    ws.onmessage = function(evt) {
        var d = $.parseJSON(evt.data);
        series.data.push([d.x, d.y]);
        while (series.data.length > datalen) {
            series.data.shift();
        }
        if(plot) {
            plot.setData([series]);
            plot.setupGrid();
            plot.draw();
        } else if(series.data.length > 10) {
            plot = $.plot($placeholder, [series], {
                xaxis:{
                    mode: "time",
                    timeformat: "%H:%M:%S",
                    minTickSize: [2, "second"],
                },
                yaxis: {
                    min: 0,
                    max: 5
                }
            });
            plot.draw();
        }
    }
    ws.onopen = function(evt) {
        $('#conn_status').html('<b>Connected</b>');
    }
    ws.onerror = function(evt) {
        $('#conn_status').html('<b>Error</b>');
    }
    ws.onclose = function(evt) {
        $('#conn_status').html('<b>Closed</b>');
    }
});

