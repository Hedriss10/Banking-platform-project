function openModal() {
    var myModal = new bootstrap.Modal(document.getElementById('registerbankers'), {
        keyboard: true 
    });
    myModal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    openModal();
});