function searchUser() {
    let searchValue = document.getElementById('searchField').value.trim();
    fetch(`/searchpromoters?query=${searchValue}`)
        .then(response => response.json())
        .then(users => {
            let tableBody = document.querySelector('#userTable tbody');
            tableBody.innerHTML = '';
            users.forEach(user => {
                let row = `<tr>
                    <td>${user.id}</td>
                    <td contenteditable="true" data-id="${user.id}" data-field="username">${user.username}</td>
                    <td contenteditable="true" data-id="${user.id}" data-field="user_identification">${user.user_identification}</td>
                    <td>
                        <select data-id="${user.id}" data-field="type_user">
                            <option value="sellers" ${user.type_user === 'sellers' ? 'selected' : ''}>Vendedor</option>
                            <option value="admin" ${user.type_user === 'admin' ? 'selected' : ''}>Administrador</option>
                            <option value="promoters" ${user.type_user === 'promoters' ? 'selected' : ''}>Promotor</option>
                        </select>
                    </td>
                </tr>`;
                tableBody.innerHTML += row;
            });
            initializeInlineEdit(); // Certifique-se de tornar editável novamente
        })
        .catch(error => console.error('Erro ao buscar usuários:', error));
}


function saveChanges() {
    document.querySelectorAll('tbody tr').forEach(row => {
        let id = row.querySelector('td:first-child').textContent.trim();
        let username = row.querySelector('[data-field="username"]').textContent.trim();
        let userIdentification = row.querySelector('[data-field="user_identification"]').textContent.trim();
        let userType = row.querySelector('select[data-field="type_user"]').value;

        fetch(`/update-promoter/${id}`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                user_identification: userIdentification,
                type_user: userType
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Atualizado com sucesso!', data.message);
                    initializeInlineEdit();
                } else {
                    throw new Error(data.error || 'Falha desconhecida ao atualizar');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
            });
    });
}

function initializeInlineEdit() {
    document.querySelectorAll('[data-field="username"], [data-field="user_identification"]').forEach(element => {
        element.setAttribute('contenteditable', 'true');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeInlineEdit();
});
