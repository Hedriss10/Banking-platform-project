document.getElementById('addBankForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const bankName = document.getElementById('bankName').value;
    
    fetch('/register-bankers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: bankName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Banco cadastrado com sucesso.')
        } else {
            alert(data.error || 'Error occurred while adding the bank');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while communicating with the server.');
    });
});
