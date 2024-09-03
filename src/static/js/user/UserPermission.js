document.addEventListener('DOMContentLoaded', function () {
    const updateButtons = document.querySelectorAll('.btn-update-permission');

    updateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const selectedPermission = document.getElementById('type_user_func').value;

            if (!selectedPermission) {
                alert('Selecione um tipo de cargo antes de alterar.');
                return;
            }

            fetch(`/alter-permission/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type_user_func: selectedPermission })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Permissão atualizada com sucesso!');
                    location.reload(); 
                } else {
                    alert('Erro ao atualizar permissão: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao atualizar permissão.');
            });
        });
    });
});
