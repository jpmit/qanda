// qapage.js
// Any javascript code that handles the DOM.

'use strict';

/*jslint browser:true */

var qa = qa || {};

qa.page = (function () {
    var sendform = document.getElementById("sendmessage"),
        handleEdit = document.getElementById("editableHandle"),
        myhandleDiv = document.getElementById("myhandle"),
        mymsg = document.getElementById("msgtxt"),
        replyid;

    function setMyIdHandle(id, handle) {
        // store my id
        qa.myid = id;
        // write handle to the editable text box
        handleEdit.value = handle;
        // write handle name to the list of users
        myhandleDiv.innerHTML = handle;
    }

    handleEdit.onkeyup = function () {
        setMyIdHandle(qa.myid, handleEdit.value);
    };
    // we send the message to the server onchange i.e. only when
    // handleEdit loses focus.
    handleEdit.onchange = function () {
        qa.send({'mtype': 'changehandle',
                 'handle': handleEdit.value});
    };

    function addNewHandle(id, handle) {
        var handlesDiv = document.getElementById('handles'),
            hdiv = document.createElement('div');
        // store the user id
        qa.currentUsers[id] = handle;
        // add user div to the document
        hdiv.id = "user" +  id;
        hdiv.innerHTML = handle;
        handlesDiv.appendChild(hdiv);
    }

    function removeHandle(id) {
        var handleDiv = document.getElementById("user" + id);
        // remove from store
        delete qa.currentUsers[id];
        // remove from document
        handleDiv.parentNode.removeChild(handleDiv);
    }

    // draw a message on the HTML document
    function addmessage(msg, depth) {
        var pdivId,
            pdiv,
            qdiv,
            padHTML = "",
            i;
        // store the message
        msg.depth = depth;
        qa.allMessages[msg.id] = msg;

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
        qdiv.innerHTML = padHTML + "[" + msg.user + "]" + msg.posttime + "</br>" + padHTML + msg.message + "<a href=javascript:void(0) onclick=qa.page.setReplyId(" + msg.id + ");>Reply</a>";
        // add the div
        pdiv.appendChild(qdiv);
    }

    function setReplyId(msgid) {
        var msg = qa.allMessages[msgid.toString()];
        if (replyid !== undefined) {
            document.getElementById("msg" + replyid).style.color = "black";
        }
        // set replyid in outer scope
        replyid = msgid;
        // display the msg id and message to reply to above the text box
        document.getElementById("replyuser").innerHTML = msg.user + " wrote:";
        document.getElementById("replymessage").innerHTML = msg.message;
        // display the text box
        sendform.style.display = 'block';
        // highlight the question we selected a reply to
        document.getElementById("msg" + msgid).style.color = "red";
    }

    // send message
    sendform.style.display = 'none';
    sendform.onsubmit = function () {
        var txt = mymsg.value,
            msg = {'mtype': 'response', 'text': txt, 'replyid': replyid};
        qa.send(msg);
        mymsg.value = '';
        return false; // don't refresh page
    };

    return {'setMyIdHandle': setMyIdHandle,
            'addNewHandle': addNewHandle,
            'removeHandle': removeHandle,
            'addmessage': addmessage,
            'setReplyId': setReplyId};
}());
