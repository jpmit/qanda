// qafills.js
// PolyFills that implement any functionality that the client might not have.

'use strict';
/*jslint browser:true */

// set Date.now (for timestamp for engines that don't support it)
if (!Date.now) {
    Date.now = function now() {
        return new Date().getTime();
    };
}

// http://stackoverflow.com/questions/4793604/
document.insertAfter = function (referenceNode, newNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
};

