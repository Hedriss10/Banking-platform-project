function showUpdateBlockModal(element) {
    var userId = element.getAttribute('data-userid');
    document.getElementById('userIdBlock').value = userId; // Corrigindo ID para evitar conflito
    $('#showUpdateBlockModal').modal('show');
  }
  
  document.getElementById('updateBlockUserForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const userId = document.getElementById('userIdBlock').value;
    fetch(`/update-promoter/block/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Usuário bloqueado com sucesso!');
        $('#showUpdateBlockModal').modal('hide');
      } else {
        alert('Erro ao bloquear o usuário: ' + data.message);
      }
    })
    .catch(error => alert('Erro ao bloquear o usuário: ' + error));
  });
  