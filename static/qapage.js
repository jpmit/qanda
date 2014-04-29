// qapage.js
// Any javascript code that handles the DOM.

'use strict';

/*jslint browser:true */

var qa = qa || {};

qa.page = (function () {
    var sendform = document.getElementById("sendmessage"),
        replydiv = document.getElementById("replydiv"),
        handleEdit = document.getElementById("editableHandle"),
        myhandleDiv = document.getElementById("myhandle"),
        addQuestionButton = document.getElementById("addquestion"),
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
        var pDivId,
            pDiv,
            messageDiv = document.createElement('div'),
            userSpan = document.createElement('span'),
            timeSpan = document.createElement('span'),
            textDiv = document.createElement('div'),
            replySpan = document.createElement('span'),
            padHTML = "",
            i;
        // store the message
        msg.depth = depth;
        qa.allMessages[msg.id] = msg;

        // get the parent div
        if (msg.parentid === qa.rootParentId) {
            pDivId = "questiontree";
        } else {
            pDivId = "msg" + msg.parentid;
        }
        pDiv = document.getElementById(pDivId);
        // the message div
        messageDiv.className = "not_selected";
        messageDiv.id = "msg" + msg.id;
        messageDiv.style.paddingLeft = "" + 10 * depth + "px";
        // user who posted the message
        userSpan.className = "message_user";
        userSpan.innerHTML = msg.user;
        // time the message was posted
        timeSpan.innerHTML = " " + msg.posttime;
        // the actual message text itself
        textDiv.className = "message_text";
        textDiv.innerHTML = msg.message;
        // the reply link
        replySpan.className = "message_reply";
        replySpan.innerHTML = "<a href=javascript:void(0) onclick=qa.page.showReplyDiv(" + msg.id + ");>Reply</a>";

        messageDiv.appendChild(userSpan);
        messageDiv.appendChild(timeSpan);
        messageDiv.appendChild(textDiv);
        messageDiv.appendChild(replySpan);
        pDiv.appendChild(messageDiv);
    }

    function showReplyDiv(msgid) {
        console.log(msgid);
        var parentMsg,
            replyMessage;
        if (msgid === qa.rootParentId) {
            replyMessage = "Add new question";
            document.getElementById("replybutton").value = "Post";
        } else {
            parentMsg = qa.allMessages[msgid.toString()];
            replyMessage = parentMsg.user + " wrote: " + parentMsg.message;
            document.getElementById("replybutton").value = "Reply";
        }

        if (replyid !== undefined && replyid !== qa.rootParentId) {
            document.getElementById("msg" + replyid).className = "not_selected";
        }
        // set replyid in outer scope
        replyid = msgid;
        // message above the reply box
        document.getElementById("replymessage").innerHTML = replyMessage;
        // display the text box
        replydiv.style.display = 'block';
        // highlight the question we selected a reply to
        if (msgid !== qa.rootParentId) {
            document.getElementById("msg" + msgid).className = "selected";
        }
    }

    // send message
    replydiv.style.display = 'none';
    sendform.onsubmit = function () {
        var txt = mymsg.value,
            msg = {'mtype': 'response', 'text': txt, 'replyid': replyid};
        qa.send(msg);
        mymsg.value = '';
        replydiv.style.display = 'none';
        return false; // don't refresh page
    };

    addQuestionButton.onclick = function () {showReplyDiv(qa.rootParentId);}

    return {'setMyIdHandle': setMyIdHandle,
            'addNewHandle': addNewHandle,
            'removeHandle': removeHandle,
            'addmessage': addmessage,
            'showReplyDiv': showReplyDiv};
}());
