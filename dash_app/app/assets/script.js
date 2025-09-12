window.addEventListener('beforeunload', function (event) {
    fetch('/client-close', { method: 'POST' });
});