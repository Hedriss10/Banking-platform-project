function openModal() {
    var myModal = new bootstrap.Modal(document.getElementById('registroPontoModal'), {
        keyboard: true 
    });
    myModal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    openModal();
});