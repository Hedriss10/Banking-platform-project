document.addEventListener('DOMContentLoaded', function() {
    const importForm = document.getElementById('importUser');

    importForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData();
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
            alert('Erro ao comunicar com o servidor: ' + error.message);
        });
    });
});
