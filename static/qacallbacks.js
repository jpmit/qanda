// qacallbacks.js
// Callback functions that handle messages received from the server,
// and anything needed to assist these functions.

var qa = qa || {};

qa.callbacks = (function () {

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
        'newmessage': newmessageCall
    };
    ws.setCallBacks(cbacks);

    function myhandleCall(resp) {
        qa.page.setMyIdHandle(resp.myid, resp.handle);
    }

    function fulltreeCall(resp) {
        var i,
            j,
            tree = resp.tree,
            currId,
            children;
        // populate the page
        for (i = 0; i !== tree.rootnodes.length; i += 1) {
            currId = "" + tree.rootnodes[i];
            // depth first descent
            addMessageDfs(tree, tree.messages[currId], 0);
        }
    }

    function newhandleCall(resp) {
        qa.page.addNewHandle(resp.id, resp.handle);
    }

    function addMessageDfs(tree, msg, depth) {
        var q = [msg];
        while (q.length > 0) {
            msg = q.shift();
            // add this particular message to the page
            qa.page.addmessage(msg, depth);
            // recursively call this function for all my children
            tree.children[msg.id].forEach(function(element, index, array) {
                addMessageDfs(tree, tree.messages["" + element], depth + 1);
            });
        }
    }

    function removehandleCall(resp) {
        qa.page.removeHandle(resp.id);
    }

    function newmessageCall(resp) {
        // get message depth
        if (resp.message.parentid === -1) {
            depth = 0;
        } else {
            depth = qa.allMessages[resp.message.parentid].depth + 1;
        }
        qa.page.addmessage(resp.message, depth);
    }
    
    return {};
}());
