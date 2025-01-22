class ManageUsers {
    constructor() {
        this.urlSearch = '/users';
        this.searchInput = document.getElementById('searchInput');
        this.tbody = document.querySelector('tbody');

        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.searchUsers());
        } else {
            console.error('Elemento searchInput não encontrado na página.');
        }
    }

    async searchUsers() {
        const searchTerm = this.searchInput.value.trim().toLowerCase();

        try {
            const url = new URL(this.urlSearch, window.location.origin);
            url.searchParams.append('search', searchTerm);

            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro na resposta do servidor');
            }

            const data = await response.json();

            this.updateTable(data.users);
        } catch (error) {
            console.error('Erro ao buscar dados:', error);
            this.displayError('Erro ao carregar dados dos usuários. Tente novamente.');
        }
    }

    updateTable(users) {
        this.tbody.innerHTML = '';

        if (users.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `<td colspan="8" class="text-center">Nenhum usuário encontrado</td>`;
            this.tbody.appendChild(emptyRow);
            return;
        }

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.lastname}</td>
                <td>${user.cpf}</td>
                <td>${user.role}</td>
                <td>${user.email}</td>
                <td><i class="fas fa-ban cursor-pointer" data-userid="${user.id}" onclick="showUpdateBlockModal(this)"></i></td>
                <td><i class="fas fa-edit cursor-pointer" data-userid="${user.id}" onclick="showUpdateUserModal(this)"></i></td>
                <td><i class="fas fa-trash-alt cursor-pointer" data-userid="${user.id}" onclick="showDeleteModal(this)"></i></td>
            `;
            this.tbody.appendChild(row);
        });
    }

    displayError(message) {
        this.tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">${message}</td>
            </tr>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const usersManager = new ManageUsers();
    usersManager.searchUsers();
});
