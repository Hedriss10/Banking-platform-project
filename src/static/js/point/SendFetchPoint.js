function submitForm() {
    const dayHourInput = document.getElementById('dataHora');
    const typeSelect = document.getElementById('tipo');


    if (!dayHourInput.value) {
        alert('Por favor, preencha a data e hora.');
        return;
    }

    const dayHour = dayHourInput.value;
    const type = typeSelect.value;

    const data = {
        'day_hour': dayHour,
        'type': type
    };

    fetch('/registerpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 
        },
        body: JSON.stringify(data),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        console.log('Success:', result);
        alert('Registro salvo com sucesso!');
        const modalElement = document.getElementById('registroPontoModal');
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        modalInstance.hide();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Falha ao salvar o registro.');
    });
}
