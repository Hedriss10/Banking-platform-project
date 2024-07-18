document.addEventListener('DOMContentLoaded', function () {
    var alerts = document.querySelectorAll('.btn-close');
    alerts.forEach(function (closeButton) {
        closeButton.addEventListener('click', function () {
            var alert = this.parentElement;
            alert.style.display = 'none';
            if (alert.parentElement.children.length === 1) {
                alert.parentElement.style.display = 'none';
            }
        });
    });
});