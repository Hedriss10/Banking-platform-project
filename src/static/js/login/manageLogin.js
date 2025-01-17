class ManagerLogin {
    constructor() {
        this.url_login = '/login';
        this.url_password = '/update-password';
    }

    setupUpdatePassword() {
        document.getElementById('updatePasswordForm').addEventListener('submit', (e) => {
            e.preventDefault();

            const formData = {
                userId: document.getElementById('userId').value,
                newPassword: document.getElementById('newPassword').value,
                email: document.getElementById("email").value,
            };

            fetch(this.url_password, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
                .then((response) => response.json())
                .then((data) => {
                    const notification = document.getElementById('notification');
                    if (data.success) {
                        notification.className = 'alert alert-success';
                        notification.innerText = data.message;
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                    } else {
                        notification.className = 'alert alert-danger';
                        notification.innerText = data.error || 'Erro ao atualizar a senha';
                    }
                    notification.style.display = 'block';
                })
                .catch((error) => {
                    console.error('Error:', error);
                    const notification = document.getElementById('notification');
                    notification.className = 'alert alert-danger';
                    notification.innerText = 'Ocorreu um erro ao atualizar a senha';
                });
        });
    }

    setupLogin() {
        document.getElementById('SendLoginUser').addEventListener('submit', (e) => {
            e.preventDefault();

            const email = document.getElementById('emailLogin').value;
            const password = document.getElementById('passwordLogin').value;

            fetch(this.url_login, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            })
                .then((response) => response.json())
                .then((data) => {
                    const notification = document.getElementById('notification');
                    if (data.success) {
                        alert('Seja bem-vindo!');
                        // Redirecionar para a página operacional, se necessário
                        // window.location.href = '/operational';
                    } else {
                        notification.className = 'alert alert-danger';
                        notification.innerText = data.error || 'Erro ao logar';
                        notification.style.display = 'block';
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    const notification = document.getElementById('notification');
                    notification.className = 'alert alert-danger';
                    notification.innerText = 'Erro ao tentar logar!';
                    notification.style.display = 'block';
                });
        });
    }
}

const managerLogin = new ManagerLogin();
managerLogin.setupUpdatePassword();
managerLogin.setupLogin();
