// callbacks.js
// Callbacks for the various message 'types', for use with
// websocket.js, and tracking of the client id.

var CALL = (function () {

    // the client id, set by the server and sent in all messages to
    // the server.
    var id = null,
    // handle (username)
       handle = "",
       sendform,
       qtree,
       replyid,
       allmessages = {};

    // callbacks for the different message types that can be RECEIVED
    // from server with the websocket interface.
    var cbacks = {
        // we receive handle (username) and fulltree on open
        'myhandle': myhandle,
        'fulltree': fulltree,
        // received when a someone new enters the room
        'newhandle': newhandle,
        // received when someone leaves the room
        'removehandle': removehandle,
        // received when a new message is posted
        'newmessage': newmessage
    };
    WS.setCallBacks(cbacks);

    // set Date.now (for timestamp for engines that don't support it)
    if (!Date.now) {
        Date.now = function now() {
            return new Date().getTime();
        };
    }

    // used to send a message, this simply adds the client id and
    // timestamp to the object, and sends a string of the data.
    function send(message) {
        message.id = id;
        message.tstamp = Date.now();
        WS.send(JSON.stringify(message));
    }

    // send message
    sendform = document.getElementById("sendmessage");
    mymsg = document.getElementById("msgtxt");
    sendform.style.display = 'none';
    sendform.onsubmit = function () { 
        var txt = mymsg.value,
            msg = {'mtype': 'response', 'text': txt, 'replyid': replyid}
        send(msg);
        mymsg.value = '';
        return false; // don't refresh page
    };

    function newmessage(resp) {
        // get message depth
        if (resp.message.parentid === -1) {
            depth = 0;
        } else {
            depth = allmessages[resp.message.parentid].depth + 1;
        }
        addmessage(resp.message, depth);
    }

    // callback functions for received messages
    function myhandle(resp) {
        id = resp.myid;
        handle = resp.handle;
        document.getElementById("myhandle").innerHTML = handle;
    }

    function setReplyId(msgid) {
        console.log(msgid);
        var rply,
            msg = allmessages["" + msgid];
        // set replyid in outer scope
        replyid = msgid;
        // display the msg id and message to reply to above the text box
        document.getElementById("replyuser").innerHTML = msg.user + " wrote:";
        document.getElementById("replymessage").innerHTML = msg.message;
        // display the text box
        sendform.style.display = 'block';
    }

    // draw a message on the HTML document
    function addmessage(msg, depth) {
        var pdivId,
            pdiv,
            qdiv,
            padHTML = "",
            i;
        // get the parent div
        if (msg.parentid === -1) {
            pdivId = "questiontree";
        } else {
            pdivId = "msg" + msg.parentid;
        }
        pdiv = document.getElementById(pdivId);
        qdiv = document.createElement('div');
        qdiv.id = "msg" + msg.id;
        // hacky way to indent question responses (should use CSS)
        console.log(depth);
        for (i = 0; i < depth; i += 1) {
            padHTML += "&nbsp;&nbsp;&nbsp;&nbsp;";
        }
        qdiv.innerHTML = padHTML + "[" + msg.user + "]<br\>" + padHTML + msg.message + "<a href=javascript:void(0) onclick=CALL.setReplyId(" + msg.id + ");>Reply</a>";
        // add the div
        pdiv.appendChild(qdiv);

        // add to internal store
        msg.depth = depth;
        allmessages[msg.id] = msg;
    }

    function addMessageDfs(tree, msg, depth) {
        var q = [msg];
        while (q.length > 0) {
            msg = q.shift();
            // add this particular message to the page
            addmessage(msg, depth);
            // recursively call this function for all my children
            tree.children[msg.id].forEach(function(element, index, array) {
                addMessageDfs(tree, tree.messages["" + element], depth + 1);
            });
        }
    }

    function fulltree(resp) {
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

    function newhandle(resp) {
        var handlesDiv = document.getElementById('handles'),
            hdiv = document.createElement('div');
        hdiv.innerHTML = resp.handle;
        handlesDiv.appendChild(hdiv);
    }

    function removehandle(resp) {
    }

    // Public API
    return {'send': send,
            'setReplyId': setReplyId};

}());
