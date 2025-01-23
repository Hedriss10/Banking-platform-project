class ManageUsers {
    constructor() {
        this.urlSearch = '/list-users';
        this.searchInput = document.getElementById('searchInput');
        this.tbody = document.querySelector('tbody');
        this.paginationContainer = document.querySelector('.pagination');

        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.searchUsers());
        } else {
            console.error('Elemento searchInput não encontrado na página.');
        }
    }

    async searchUsers(page = 1) {
        const searchTerm = this.searchInput.value.trim().toLowerCase();

        try {
            const url = new URL(this.urlSearch, window.location.origin);
            url.searchParams.append('search', searchTerm);
            url.searchParams.append('page', page);

            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.status !== 200) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro na resposta do servidor');
            }

            const data = await response.json();
            console.log('Dados recebidos:', data); // Log para depuração

            this.updateTable(data.users);
            this.updatePagination(data.pagination);
        } catch (error) {
            console.error('Erro ao buscar dados:', error);
            this.displayError('Erro ao carregar dados dos usuários. Tente novamente.');
        }
    }

    async updateTable(users) {
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
                <td><i class="fas fa-user-check cursor-pointer" data-userid="${user.id}" onclick="showUpdateActiveModal(this)"></i></td>
                <td><i class="fas fa-trash-alt cursor-pointer" data-userid="${user.id}" onclick="showDeleteModal(this)"></i></td>
            `;
            this.tbody.appendChild(row);
        });
    }

    async updatePagination(pagination) {
        this.paginationContainer.innerHTML = '';

        if (pagination.total_pages <= 1) return;

        const createPageItem = (page, label, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.textContent = label;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                if (!disabled) this.searchUsers(page);
            });
            li.appendChild(a);
            return li;
        };

        this.paginationContainer.appendChild(createPageItem(pagination.page - 1, 'Anterior', !pagination.has_prev));

        for (let i = 1; i <= pagination.total_pages; i++) {
            this.paginationContainer.appendChild(createPageItem(i, i, false, i === pagination.page));
        }

        this.paginationContainer.appendChild(createPageItem(pagination.page + 1, 'Próximo', !pagination.has_next));
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
