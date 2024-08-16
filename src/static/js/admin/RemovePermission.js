document.getElementById('removePermissionsButton').addEventListener('click', function(event) {
    event.preventDefault();

    var checkboxes = document.querySelectorAll('input[name="permissions_to_remove[]"]:checked');
    
    if (checkboxes.length === 0) {
        alert('Por favor, selecione pelo menos uma permissão para remover.');
        return;
    }

    var confirmation = confirm('Você tem certeza que deseja remover as permissões selecionadas?');
    if (confirmation) {
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false;
        });

        var form = document.getElementById('permissionsForm');
        var formData = new FormData(form);

        // Debug: Verificar se os dados estão sendo capturados corretamente
        formData.forEach((value, key) => {
            console.log(key + ': ' + value);
        });

        fetch("/remove-permissions", {
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
                alert('Permissões removidas com sucesso!');
                window.location.reload();
            } else {
                alert('Ocorreu um erro ao remover as permissões.');
            }
        })
        .catch(error => console.error('Erro:', error));
    }
});
