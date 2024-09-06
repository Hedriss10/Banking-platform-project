function createRoom() {
    const roomName = document.getElementById('create_room').value;
    const status = document.getElementById('status').value;

    fetch('/create_room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ create_room: roomName, status: status }),
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            listRooms();
        })
        .catch(error => console.error('Erro ao criar sala:', error));
}


