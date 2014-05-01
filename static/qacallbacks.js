// qacallbacks.js
// Callback functions that handle messages received from the server,
// and anything needed to assist these functions.

'use strict';
/*global ws*/

var qa = qa || {};

qa.callbacks = (function () {

    function myhandleCall(resp) {
        qa.page.setMyIdHandle(resp.userid, resp.handle, resp.auth_token);
        // send back a response to the server with the topic id
        qa.send({'mtype': 'settopic'});
    }

    function newhandleCall(resp) {
        qa.page.addNewHandle(resp.userid, resp.handle);
    }

    function addMessageDfs(tree, msg, depth) {
        var q = [msg];

        while (q.length > 0) {
            msg = q.shift();
            // add this particular message to the page
            qa.page.addmessage(msg, depth);
            // recursively call this function for all my children
            tree.children[msg.id].forEach(function (element) {
                addMessageDfs(tree, tree.messages[element.toString()], depth + 1);
            });
        }
    }

    // this gets executed only once, when we first visit the page
    function fulltreeCall(resp) {
        var i,
            tree = resp.tree,
            currId;
        // populate the page
        for (i = 0; i !== tree.rootnodes.length; i += 1) {
            currId = tree.rootnodes[i].toString();
            // depth first descent
            addMessageDfs(tree, tree.messages[currId], 0);
        }
    }

    function removehandleCall(resp) {
        qa.page.removeHandle(resp.userid);
    }

    function newmessageCall(resp) {
        qa.page.addmessage(resp.message);
    }

    function changehandleCall(resp) {
        qa.currentUsers[resp.changeid.toString()] = resp.newhandle;
        qa.page.changeHandle(resp.changeid, resp.newhandle);
    }

    // callbacks for the different message types that can be received
    // from server.
    var cbacks = {
        // we receive handle (username) and fulltree on open
        'myhandle': myhandleCall,
        'fulltree': fulltreeCall,
        // received when a someone new enters the room
        'newhandle': newhandleCall,
        // received when someone leaves the room
        'removehandle': removehandleCall,
        // received when a new message is posted
        'newmessage': newmessageCall,
        // received when *another* client has changed their handle
        'changehandle': changehandleCall
    };
    ws.setCallBacks(cbacks);

    return {};
}());
