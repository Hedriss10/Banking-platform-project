function searchUser() {
    let searchValue = document.getElementById('searchField').value.trim();
    fetch(`/searchpromoters?query=${searchValue}`)
        .then(response => response.json())
        .then(users => {
            let tableBody = document.querySelector('#userTable tbody');
            tableBody.innerHTML = '';
            users.forEach(user => {
                let row = `<tr>
                    <td><input type="checkbox" value="${user.id}" class="user-checkbox"></td>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.user_identification}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error('Erro ao buscar usuários:', error));
}

function toggleUserSelection(source) {
    document.querySelectorAll('.user-checkbox').forEach(checkbox => {
        checkbox.checked = source.checked;
    });
}

function deleteSelectedUsers() {
    document.querySelectorAll('.user-checkbox:checked').forEach(checkbox => {
        fetch(`/deletepromoters/${checkbox.value}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(data.message);
                    checkbox.closest('tr').remove(); // Remove a linha da tabela
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(error => console.error('Erro ao deletar usuário:', error));
    });
}
