document.addEventListener('DOMContentLoaded', function () {
    const notificationBadge = document.getElementById('notification-badge');
    const notificationTitle = document.getElementById('notification-title');
    const notificationList = document.getElementById('notification-list'); // Seleciona o <ul> para as notificações

    function fetchAvailableContracts() {
        fetch(`/operational/available-contracts-count`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            const availableContracts = data.available_contracts;

            notificationBadge.textContent = availableContracts;
            notificationTitle.textContent = `Você tem ${availableContracts} contratos disponíveis para digitar`;

            if (availableContracts === 0) {
                notificationList.innerHTML = `<li class="text-center">Nenhum contrato disponível para digitar</li>`;
            } else {
                notificationList.innerHTML = ''; // Limpa as notificações antigas
                for (let i = 1; i <= availableContracts; i++) {
                    notificationList.innerHTML += `
                        <li class="notification-item">
                            <i class="bi bi-check-circle text-success"></i>
                            <div>
                                <h4>Contrato Disponível ${i}</h4>
                                <p>Você tem um contrato disponível para digitar.</p>
                            </div>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                    `;
                }
            }
        })
        .catch(error => console.error('Erro ao buscar dados:', error));
    }

    // Carrega a contagem inicial de propostas ao carregar a página
    fetchAvailableContracts();

    // Atualiza a contagem a cada minuto (60000 ms)
    setInterval(fetchAvailableContracts, 60000);
});
