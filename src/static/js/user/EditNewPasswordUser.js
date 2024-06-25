function showUpdatePasswordModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userId').value = userId;
    $('#updatePasswordModal').modal('show');
  }
  
  // Função para gerar uma senha aleatória
  function generatePassword() {
    const length = 12; // Comprimento da senha
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let password = "";
    for (let i = 0; i < length; i++) {
      let randomIndex = Math.floor(Math.random() * charset.length);
      password += charset[randomIndex];
    }
    document.getElementById('newPassword').value = password;
    alert("Senha gerada: " + password);
  }
  
  // Função para submeter o formulário de atualização de senha
  document.getElementById('updatePasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const newPassword = document.getElementById('newPassword').value;
    const userId = document.getElementById('userId').value;
    fetch(`/update-promoter/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: newPassword })
    })
    .then(response => response.json())
    .then(data => alert('Senha atualizada com sucesso!'))
    .catch(error => alert('Erro ao atualizar senha'));
  });