document.addEventListener('DOMContentLoaded', function () {
    setupUserRegistration();
    setupDeleteUser();
    setupUpdatePassword();
    setupSearchUser();
    showUpdateBlockModal();

});

function setupUserRegistration() {
    const importForm = document.getElementById('importUser');
    importForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(this);
        formData.append('username', document.getElementById('username').value);
        formData.append('lastname', document.getElementById('lastname').value);
        formData.append('user_identification', document.getElementById('user_identification').value);
        formData.append('password', document.getElementById('password').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('type_user_func', document.getElementById('type_user_func').value);
        formData.append('extension', document.getElementById('extension').value);
        formData.append('extension_room', document.getElementById('extension_room').value);

        fetch('/registerpromoters', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Usuário cadastrado com sucesso!');
                    window.location.reload();
                } else {
                    alert('Erro ao adicionar o usuário: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Cadastrado com sucesso!');
                window.location.reload();
            });
    });
}

function setupDeleteUser() {
    document.getElementById('deleteUserForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const userId = document.getElementById('userIdDelete').value;
        fetch(`/deletepromoters/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Usuário deletado com sucesso!');
                    $('#showDeleteModal').modal('hide');
                } else {
                    alert('Erro ao deletar o usuário: ' + data.message);
                }
            })
            .catch(error => alert('Erro ao deletar o usuário: ' + error));
    });
}

function setupUpdatePassword() {
    document.getElementById('updatePasswordForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const newPassword = document.getElementById('newPassword').value;
        const userId = document.getElementById('userId').value;
        fetch(`/update-promoter/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: newPassword })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Senha atualizada com sucesso!');
                } else {
                    alert('Erro ao atualizar senha: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro ao atualizar senha', error);
                alert('Erro ao comunicar com o servidor: ' + error.message);
            });
    });
}

function setupSearchUser() {
    document.getElementById('searchField').addEventListener('input', function () {
        let searchValue = this.value.trim();
        if (searchValue.length > 2) { // Assuming at least 3 characters for search to proceed
            fetch(`/searchpromoters?query=${searchValue}`)
                .then(response => response.json())
                .catch(error => console.error('Erro ao buscar usuários:', error));
        }
    });
}

// Utilize esta função para mostrar os modais de exclusão ou atualização de senha
function showModal(modalId, userId) {
    document.getElementById('userIdDelete').value = userId; // Assume the same field for delete and update
    $(`#${modalId}`).modal('show');
}

// Função para gerar uma senha aleatória
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


// Function shwoUpdatePasswordModal
function showUpdatePasswordModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userId').value = userId;
    $('#updatePasswordModal').modal('show');
}

// Function generator random password
function generatePassword() {
    const length = 12; // Compress password
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let password = "";
    for (let i = 0; i < length; i++) {
        let randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
    }
    document.getElementById('newPassword').value = password;
    alert("Senha gerada: " + password);
}


// function for block user 
function showUpdateBlockModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdBlock').value = userId; // Corrigindo ID para evitar conflito
    $('#showUpdateBlockModal').modal('show');
}


// Function for active user, then is blocked 
function showUpdateActiveModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdActive').value = userId;
    $('#showUpdateActiveModal').modal('show');
}

// function for delete user select 
function showDeleteModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdDelete').value = userId;
    $('#showDeleteModal').modal('show');
}


// Event for new password or generator password for user 
document.getElementById('updatePasswordForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const newPassword = document.getElementById('newPassword').value;
    const userId = document.getElementById('userId').value;
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


// Event for new block user, line red
document.getElementById('updateBlockUserForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const userId = document.getElementById('userIdBlock').value;
    fetch(`/update-promoter/block/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Usuário bloqueado com sucesso!');
                $('#showUpdateBlockModal').modal('hide');
            } else {
                alert('Erro ao bloquear o usuário: ' + data.message);
            }
        })
        .catch(error => alert('Erro ao bloquear o usuário: ' + error));
});


// event updateactiveuserform 
document.getElementById('updateActiveUserForm').addEventListener('submit', function (e) {
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



// event delete user select 
document.getElementById('deleteUserForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const userId = document.getElementById('userIdDelete').value;
    fetch(`/deletepromoters/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Usuário deletado com sucesso!');
                $('#showDeleteModal').modal('hide'); // Fechar o modal correto
                window.location.reload();
                // Recarregar a página ou remover a linha da tabela via JavaScript
            } else {
                alert('Erro ao deletar o usuário: ' + data.message);
            }
        })
        .catch(error => alert('Erro ao deletar o usuário: ' + error));
});