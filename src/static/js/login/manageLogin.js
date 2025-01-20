class ManagerLogin {
    constructor() {
        this.url_login = '/login'; // rotas do backend
        this.url_password = '/update-password'; // rotas do backend
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.className = `alert alert-${type}`;
        notification.innerText = message;
        notification.classList.remove('d-none');
        setTimeout(() => {
            notification.classList.add('d-none');
        }, 5000);
    }

    async setupUpdatePassword() {
        document.getElementById('updatePasswordForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                userId: document.getElementById('userId').value,
                newPassword: document.getElementById('newPassword').value,
                email: document.getElementById("email").value,
            };

            try {
                const response = await fetch(this.url_password, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                if (!response.ok) {
                    if (response.status === 400) {
                        throw new Error('Dados inválidos. Verifique e tente novamente.');
                    }
                    throw new Error(`Erro: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    this.showNotification(data.message, 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    this.showNotification(data.error || 'Erro ao atualizar a senha', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification(error.message || 'Ocorreu um erro ao atualizar a senha', 'danger');
            }
        });
    }

    async setupLogin() {
        document.getElementById('SendLoginUser').addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append("cpfLogin", document.getElementById('cpfLogin').value).trim();
            formData.append("passwordLogin", document.getElementById('passwordLogin').value);


            if (!cpfLogin || !passwordLogin) {
                this.showNotification('CPF e senha são obrigatórios!', 'warning');
                return;
            }

            try {
                const response = await fetch(this.url_login, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                if (!response.ok) {
                    if (response.status === 400) {
                        throw new Error('CPF ou senha inválidos. Tente novamente.');
                    }
                    throw new Error(`Erro: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    this.showNotification('Seja bem-vindo!', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard'; // Redireciona após o login
                    }, 2000);
                } else {
                    this.showNotification(data.error || 'Erro ao logar', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification(error.message || 'Erro ao tentar logar!', 'danger');
            }
        });
    }
}

document.addEventListener("DocumentContentLoaded", function() {
    const managerLogin = new ManagerLogin();
    managerLogin.setupUpdatePassword();
    managerLogin.setupLogin();
});
