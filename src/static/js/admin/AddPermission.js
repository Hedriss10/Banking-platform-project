document.getElementById('savePermissionsButton').addEventListener('click', function(event) {
    event.preventDefault();
    
    var form = document.getElementById('permissionsForm');
    var formData = new FormData(form);

    fetch("/admin/permissions/bulk", {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.redirected) {
            console.error("Redirecionamento detectado:", response.url);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Permissões atualizadas com sucesso!');
            window.location.reload();
        } else {
            alert('Ocorreu um erro ao atualizar as permissões.');
        }
    })
    .catch(error => console.error('Erro:', error));
});
