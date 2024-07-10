document.addEventListener('DOMContentLoaded', function() {
    var proposalForm = document.getElementById('proposalForm');

    proposalForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var formData = new FormData(proposalForm);
        var data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        fetch('/proposal/new-proposal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })

        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
