function setupUpdatePassword() {
    document.getElementById('updatePasswordForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append("userId", document.getElementById('userId').value);
        formData.append("newPassword", document.getElementById('newPassword').value);


        fetch('/update-user', {
            method: 'POST',
            body: formData,
            headers: {
                emai: document.getElementById("email").value
            }
        })
        .then(response => response.json())  // Diretamente processa o JSON
        .then(data => {
            const notification = document.getElementById('notification');
            if (data.success) {
                // Exibir a notificação de sucesso
                notification.className = 'alert alert-success';
                notification.innerText = data.message;
                setTimeout(() => { window.location.reload();}, 3000)
            } else {
                // Exibir a notificação de erro
                notification.className = 'alert alert-danger';
                notification.innerText = data.error || 'Erro ao atualizar a senha';
            }
            notification.style.display = 'block'; // Exibe a notificação
            
            // Opcional: Ocultar a notificação após 3 segundos
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        })
        .catch(error => {
            console.error('Erro ao atualizar senha', error);
            const notification = document.getElementById('notification');
            notification.className = 'alert alert-danger';
            notification.innerText = 'Erro ao comunicar com o servidor: ' + error.message;
            notification.style.display = 'block'; // Exibe a notificação
            
            // Opcional: Ocultar a notificação após 3 segundos
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        });
    });
}

document.addEventListener('DOMContentLoaded', setupUpdatePassword);
