function setupUpdatePassword() {
    document.getElementById('updatePasswordForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append("userId", document.getElementById('userId').value);
        formData.append("newPassword", document.getElementById('newPassword').value);

        fetch('/update-promoter', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Erro na resposta do servidor.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Senha atualizada com sucesso!');
                window.location.reload;
            } else {
                alert('Erro ao atualizar senha: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar senha', error);
            alert('Erro ao comunicar com o servidor: ' + error.message);
        });
    });
}

document.addEventListener('DOMContentLoaded', setupUpdatePassword);
