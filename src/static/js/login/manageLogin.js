class ManagerLogin {
    constructor() {
        this.url_login = '/login'; // rotas do backend
        this.url_password = '/new-restpassword'; // rotas do backend
    }

    // showNotification recebe duas strings para ser notificado na UI
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

                if (response.status === 200) {
                    this.showNotification('Senha atualizada!', 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect_url;                        
                    }, 1000);
                } else {
                    this.showNotification(message=data.error || 'Erro ao atualizar a senha', 'danger');
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
    
            const cpfLogin = document.getElementById('cpfLogin').value.trim();
            const passwordLogin = document.getElementById('passwordLogin').value;
    
            if (!cpfLogin || !passwordLogin) {
                this.showNotification('CPF e senha são obrigatórios!', 'warning');
                return;
            }
    
            const formData = {
                cpfLogin: cpfLogin,
                passwordLogin: passwordLogin,
            };
    
            try {
                const response = await fetch(this.url_login, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });
        
                if (response.ok) {
                    const data = await response.json();    
                    if (response.status == 200) {
                        this.showNotification('Seja bem-vindo!', 'success');
                        setTimeout(() => {
                            window.location.href = data.redirect_url;                     
                        }, 1000);
                    } else {
                        this.showNotification(data.error || 'Erro ao logar', 'danger');
                    } 
                } else {
                    const text = await response.text();
                    this.showNotification('Senha incorreta.', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification(error.message || 'Erro ao tentar logar!', 'danger');
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const managerLogin = new ManagerLogin();

    if (document.getElementById('updatePasswordForm')) {
        managerLogin.setupUpdatePassword();
    }

    if (document.getElementById('SendLoginUser')) {
        managerLogin.setupLogin();
    }
});

