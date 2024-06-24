function searchUser() {
    let searchValue = document.getElementById('searchField').value.trim();
    fetch(`/searchpromoters?query=${searchValue}`)
        .then(response => response.json())
        .then(users => {
            let tableBody = document.querySelector('#userTableGerement tbody');
            tableBody.innerHTML = '';
            users.forEach(user => {
                let row = `<tr>
                    <td>${user.name}</td>
                    <td>${user.lastname}</td>
                    <td>●●●●●●</td>
                    <td>
                        <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#updatePasswordModal" data-userid="${user.id}">
                            Atualizar Senha
                        </button>
                    </td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error('Erro ao buscar usuários:', error));
}

function generatePassword() {
    const length = 12; // Define the length of the password
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let password = "";
    for (let i = 0; i < length; i++) {
        let randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
    }
    document.getElementById('newPassword').value = password;
    alert("Senha gerada: " + password);
}

$('#updatePasswordModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var userId = button.data('userid')
    var modal = $(this)
    modal.find('.modal-body #userId').val(userId)
});

document.getElementById('updatePasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const newPassword = document.getElementById('newPassword').value;
    const userId = document.getElementById('userId').value; // ID do usuário
    fetch(`/update-promoter/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: newPassword })
    })
    .then(response => response.json())
    .then(data => alert('Senha atualizada com sucesso!'))
    .catch(error => alert('Erro ao atualizar senha'));
});