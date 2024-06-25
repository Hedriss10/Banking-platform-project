function showDeleteModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdDelete').value = userId;
    $('#showDeleteModal').modal('show');
  }
  
  document.getElementById('deleteUserForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const userId = document.getElementById('userIdDelete').value;
    fetch(`/deletepromoters/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Usuário deletado com sucesso!');
        $('#showDeleteModal').modal('hide'); // Fechar o modal correto
        // Recarregar a página ou remover a linha da tabela via JavaScript
      } else {
        alert('Erro ao deletar o usuário: ' + data.message);
      }
    })
    .catch(error => alert('Erro ao deletar o usuário: ' + error));
  });
  