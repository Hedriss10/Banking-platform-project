document.body.addEventListener('htmx:afterRequest', function (event) {
    console.log("HTMX request completed", event);

    if (event.detail.xhr.getResponseHeader("Content-Type").includes("application/json")) {
        let data = JSON.parse(event.detail.xhr.responseText);
        console.log("Dados recebidos:", data);  // Verificar no console os dados recebidos

        if (data.message) {
            const messageDiv = document.createElement('div');
            messageDiv.setAttribute('role', 'alert');
            messageDiv.innerHTML = data.message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';

            if (data.success) {
                messageDiv.classList.add('alert', 'alert-success', 'alert-dismissible', 'fade', 'show');
            } else {
                messageDiv.classList.add('alert', 'alert-danger', 'alert-dismissible', 'fade', 'show');
            }

            const responseContainer = document.getElementById('response-container');
            if (responseContainer) {
                responseContainer.innerHTML = '';
                responseContainer.appendChild(messageDiv);
            } else {
                console.error('Container de resposta não encontrado.');
            }
        } else {
            console.error('Resposta JSON não contém a propriedade "message".');
        }
    }
});
