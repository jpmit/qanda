// websocket.js
// A minimal encapsulation of the WebSocket API.

var WS = (function () {
    
    var wsUri = "ws://localhost:9500/";
    // simulated latency (one way trip time) in ms
    var simLatency = 50;
    var debug = true; // print messages sent and received to console
    var dummy = false; // if dummy, no messages sent/received
    var sendFunction;
    var onmessageFunction;
    
    var callbacks;
    var ws;

    if (dummy) {
        onmessageFunction = function () { };
        sendFunction = function () {};
    }
    else {
        onmessageFunction = function (evt) {
            var resp;
            if (debug) {
                console.log("received message: " + evt.data);
            }

            // message received should be JSON
            resp = JSON.parse(evt.data);

            // call callback function from lookup table
            callbacks[resp.mtype](resp);
            };

        sendFunction = function(msg) {
            if (debug) {
                console.log("sending message: " + msg);
            }
            ws.send(msg);
        };
    }

    // called when we receive a message
    function onmessage (evt) {
        window.setTimeout(function () {
            onmessageFunction(evt);
        }, simLatency);
    }

    // called when connection opened
    function onopen (evt) {
    }

    function onclose (evt) {
    }

    // callbacks should have keys for the different mtypes, and values
    // that are the callback functions.
    function setCallBacks (cbacks) {
        callbacks = cbacks;
    }
    
    // send a message from the client to the server
    function send (msg) {
        window.setTimeout(function () {
            sendFunction(msg);
            }, simLatency);
    }

    // web socket setup
    function init () {
        ws = new WebSocket(wsUri);
        ws.onopen = onopen;
        ws.onclose = onclose;
        ws.onmessage = onmessage;
        ws.onerror = onerror;
    }

    // public API
    return {init: init,
            setCallBacks : setCallBacks,
            send: send}
}());
