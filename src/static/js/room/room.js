// Função para criar uma nova sala
function createRoom() {
    const roomName = document.getElementById('create_room').value;
    const status = document.getElementById('status').value;

    // Verifica se o nome da sala foi preenchido
    if (!roomName) {
        alert('Por favor, insira o nome da sala.');
        return;
    }

    fetch('/create_room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ create_room: roomName, status: status }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);  // Exibe a mensagem de sucesso
            listRooms();  // Atualiza a lista de salas (você pode definir essa função no seu backend)
        } else {
            alert('Erro ao criar sala: ' + data.error);
        }
    })
    .catch(error => console.error('Erro ao criar sala:', error));
}

function deleteRoom(roomId) {
    if (confirm('Tem certeza de que deseja excluir esta sala?')) {
        fetch(`/delete_room/${roomId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                location.reload();  // Recarrega a página após a exclusão
            } else {
                alert('Erro ao excluir a sala: ' + data.error);
            }
        })
        .catch(error => console.error('Erro:', error));
    }
}