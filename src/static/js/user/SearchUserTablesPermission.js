document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();

            fetch(`/user?search=${searchTerm}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta do servidor');
                }
                return response.json();
            })
            .then(data => {
                const tbody = document.querySelector('tbody');
                tbody.innerHTML = '';

                data.forEach((user, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.username}</td>
                        <td>${user.lastname}</td>
                        <td>${user.user_identification}</td>
                        <td>${user.type_user_func}</td>
                        <td>${user.email}</td>
                        <td><button class="btn btn-primary btn-sm p-1 btn-update-permission" data-user-id=${ user.id }>Alterar Permissão</button></td> <!-- Substitua por '' caso não exista -->
                        
                    `;
                    tbody.appendChild(row);
                });

                // Exibe mensagem se nenhum resultado for encontrado
                if (data.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = `
                        <td colspan="10" class="text-center">Nenhum usuário encontrado</td>
                    `;
                    tbody.appendChild(emptyRow);
                }
            })
            .catch(error => console.error('Erro ao buscar dados:', error));
        });
    } else {
        console.error('Elemento searchInput não encontrado na página.');
    }
});