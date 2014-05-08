// websocket.js
// James Mithen
// A minimal encapsulation of the WebSocket API.
// Messages are JSON encoded before sending, and decoded on arrival.
// All received messages should have "mtype" as a key.  Each arriving message
// is passed to a callback function according to its mtype; the
// callback function can be set by calling the function ws.setCallBacks

'use strict';
/*jslint browser:true */
/*global WebSocket */

// note that ws lives in the global namespace
var ws = (function () {

    // configuation options
    var wsUri = location.origin.replace(/^http/, 'ws') + '/ws/' + document.getElementById('topicid').innerHTML,
        simLatency = 0,  // simulated latency (one way trip time) in ms
        debug = false,   // print messages sent and received to console
        dummy = false,   // if dummy, no messages sent/received
        callbacks,
        webSocket;

    function onMessageFunction(evt) {
        var resp;
        if (debug) {
            console.log("received message: " + evt.data);
        }
        if (dummy) {
            return;
        }

        // message received should be JSON
        resp = JSON.parse(evt.data);

        // call callback function from lookup table
        callbacks[resp.mtype](resp);
    }

    function sendFunction(msg) {
        if (debug) {
            console.log("sending message: " + msg);
        }
        if (dummy) {
            return;
        }
        webSocket.send(msg);
    }

    // called when we receive a message
    function onmessage(evt) {
        window.setTimeout(function () {
            onMessageFunction(evt);
        }, simLatency);
    }

    // called when websockset connection opened
    function onopen() {
        return;
    }

    // called when websockset connection closed
    function onclose() {
        return;
    }

    function onerror() {
        return;
    }

    // callbacks should have keys for the different mtypes, and values
    // that are the callback functions.
    function setCallBacks(cbacks) {
        callbacks = cbacks;
    }

    // send a message from the client to the server
    function send(msg) {
        window.setTimeout(function () {
            sendFunction(msg);
        }, simLatency);
    }

    // web socket setup
    function init() {
        webSocket = new WebSocket(wsUri);
        webSocket.onopen = onopen;
        webSocket.onclose = onclose;
        webSocket.onmessage = onmessage;
        webSocket.onerror = onerror;
    }

    // public API
    return {init: init,
            setCallBacks : setCallBacks,
            send: send};
}());
