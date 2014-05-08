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

    // topic id is a hidden element on the page
    qa.topicId = parseInt(document.getElementById("topicid").innerHTML, 10);

    function setMyIdHandle(userId, handle, authToken) {
        // store my id
        qa.userId = userId;
        // write handle to the editable text box
        handleEdit.value = handle;
        // authToken is sent with every message
        if (authToken !== undefined) {
            qa.authToken = authToken;
        }
        // write handle name to the list of users
        myhandleDiv.innerHTML = handle;
    }

    handleEdit.onkeyup = function () {
        setMyIdHandle(qa.userId, handleEdit.value);
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
        hdiv.className = "other_handle";
        hdiv.innerHTML = handle;
        handlesDiv.appendChild(hdiv);
    }

    function changeHandle(id, newhandle) {
        document.getElementById("user" + id).innerHTML = newhandle;
    }

    function removeHandle(id) {
        var handleDiv = document.getElementById("user" + id);
        // remove from store
        delete qa.currentUsers[id.toString()];
        // remove from document
        handleDiv.parentNode.removeChild(handleDiv);
    }

    // draw a message on the HTML document
    function addmessage(msg) {
        var pDivId,
            pDiv,
            messageDiv = document.createElement('div'),
            userSpan = document.createElement('span'),
            timeSpan = document.createElement('span'),
            textDiv = document.createElement('div'),
            replySpan = document.createElement('span'),
            isRoot = (msg.parentid === qa.rootParentId),
            parentmsg = isRoot ? {} : qa.allMessages[msg.parentid],
            depth = isRoot ? 0 : parentmsg.depth + 1,
            divWidth;

        // store the message
        msg.depth = depth;
        qa.allMessages[msg.id] = msg;

        // get the parent div
        if (isRoot) {
            pDivId = "questiontree";
        } else {
            pDivId = "msg" + msg.parentid;
        }
        pDiv = document.getElementById(pDivId);
        // the message div
        messageDiv.className = "message not_selected";
        messageDiv.id = "msg" + msg.id;
        if (depth > 0) {
            messageDiv.style.marginLeft = "80px";
            divWidth = Math.max(180, 500 - 80 * depth);
            messageDiv.style.width = divWidth + "px";
        }
        // user who posted the message
        userSpan.className = "message_user";
        userSpan.innerHTML = msg.user;
        if (!isRoot) {
            userSpan.innerHTML += ' > ' + parentmsg.user;
        }
        // time the message was posted
        timeSpan.className = "message_time";
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
            document.getElementById("msg" + replyid).className = "message not_selected";
        }
        // set replyid in outer scope
        replyid = msgid;
        // message above the reply box
        document.getElementById("replymessage").innerHTML = replyMessage;
        // display the text box
        replydiv.style.display = 'block';
        // highlight the question we selected a reply to
        if (msgid !== qa.rootParentId) {
            document.getElementById("msg" + msgid).className = "message selected";
        }
    }

    // send message
    replydiv.style.display = 'none';
    sendform.onsubmit = function () {
        var txt = mymsg.value,
            msg = {'mtype': 'response', 'text': txt, 'replyid': replyid};
        // set the parent div to not_selected
        if (replyid !== qa.rootParentId) {
            document.getElementById("msg" + replyid).className = "message not_selected";
        }
        qa.send(msg);
        mymsg.value = '';
        replydiv.style.display = 'none';
        return false; // don't refresh page
    };

    addQuestionButton.onclick = function () { showReplyDiv(qa.rootParentId); };

    return {'setMyIdHandle': setMyIdHandle,
            'addNewHandle': addNewHandle,
            'removeHandle': removeHandle,
            'changeHandle': changeHandle,
            'addmessage': addmessage,
            'showReplyDiv': showReplyDiv};
}());
