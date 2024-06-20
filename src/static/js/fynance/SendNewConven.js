document.getElementById('addBankConvForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const convName = document.getElementById('convName').value;
    const bankId = document.getElementById('bankerIdConv').value; 

    var data = {
        name : convName,
        bank_id : bankId
    };


    fetch('/register-convenio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Convênio cadastrado com sucesso.')
            window.location.reload();
        } else {
            alert(data.error || 'Error occurred while adding the bank');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while communicating with the server.');
    });
});
