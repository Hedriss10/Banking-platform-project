function showUpdateActiveModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdActive').value = userId;
    $('#showUpdateActiveModal').modal('show');
}

document.getElementById('updateActiveUserForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const userId = document.getElementById('userIdActive').value;
    fetch(`/update-promoter/active/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Usuário ativado com sucesso!');
            $('#showUpdateActiveModal').modal('hide');
        } else {
            alert('Erro ao ativar o usuário: ' + data.message);
        }
    })
    .catch(error => alert('Erro ao ativar o usuário: ' + error));
});
