// qa.js
// A simple question and answer webapp, implemented using Websockets.

'use strict';
/*global ws*/

// qa is the top level namespace for the webapp
var qa = qa || {};

// call send for sending a message to the server
qa.send = function (message) {
    message.id = qa.myid;
    message.tstamp = Date.now();
    ws.send(JSON.stringify(message));
};

// currentUsers maps client ids to client handles (usernames)
qa.currentUsers = {};

// allMessages key is message id, item is the message
qa.allMessages = {};
