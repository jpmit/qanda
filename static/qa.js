// qa.js
// A simple question and answer webapp, implemented using Websockets.

'use strict';
/*jslint browser:true */
/*global ws*/

// qa is the top level namespace for the webapp
var qa = qa || {};

// call send for sending a message to the server
qa.send = function (message) {
    message.userid = qa.userId;
    message.topicid = qa.topicId;
    message.auth_token = qa.authToken;
    message.tstamp = Date.now();
    ws.send(JSON.stringify(message));
};

qa.heartBeat = true;   // send regular heartbeats to the server?
qa.heartBeatT = 10000; // time (in ms) between each heartbeat

if (qa.heartBeat) {
    window.setInterval(function () {
        qa.send({'mtype': 'heartbeat'});
    }, qa.heartBeatT);
}

// currentUsers maps client ids to client handles (usernames)
qa.currentUsers = {};

// allMessages key is message id, item is the message
qa.allMessages = {};

// parent id for 'root' (top level) messages
qa.rootParentId = -1;
