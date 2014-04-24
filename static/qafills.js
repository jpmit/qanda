// qafills.js
// PolyFills that implement any functionality that the client might not have.

(function () {
    // set Date.now (for timestamp for engines that don't support it)
    if (!Date.now) {
        Date.now = function now() {
            return new Date().getTime();
        };
    }
}());
