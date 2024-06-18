function toggleConvenios(bankId) {
    var element = document.getElementById('convenios-' + bankId);
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}