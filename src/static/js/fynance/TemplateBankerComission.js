function fetchTemplates() {
    const bankerId = document.getElementById('bankSelect').value;

    fetch(`/save-report-template?banker_id=${bankerId}`)
        .then(response => response.json())
        .then(data => {
            const templateList = document.getElementById('template-list');
            const feedback = document.getElementById('feedback');

            // Limpa as mensagens de feedback
            feedback.style.display = 'none';
            templateList.innerHTML = '';

            if (data.error) {
                feedback.style.display = 'block';
                feedback.textContent = data.error;
                feedback.className = 'alert alert-danger';
                return;
            }

            if (!Array.isArray(data) || data.length === 0) {
                feedback.style.display = 'block';
                feedback.textContent = 'Nenhum template de relatório encontrado.';
                feedback.className = 'alert alert-warning';
                return;
            }

            data.forEach((template, index) => {
                const item = document.createElement('li');
                item.className = 'list-group-item list-group-item-action';
                item.innerHTML = `
                    <h5>Layout ${template['Último template importado']}</h5>
                    <ol>
                        <li><strong>Banco:</strong> ${template.Banco || 'Não especificado'}</li>
                        <li><strong>Colunas e Primeira Linha:</strong> 
                            <ul>
                                ${template.Colunas.map(coluna => `
                                    <li>
                                        ${Object.entries(coluna).map(([key, value]) => `
                                            <strong>${key}:</strong> ${value || 'Sem valor'}
                                        `).join(', ')}
                                    </li>
                                `).join('')}
                            </ul>
                        </li>
                    </ol>
                `;
                templateList.appendChild(item);
            });
        })
        .catch(error => {
            const feedback = document.getElementById('feedback');
            feedback.style.display = 'block';
            feedback.textContent = 'Erro ao buscar templates: ' + error.message;
            feedback.className = 'alert alert-danger';
        });
}

document.getElementById('bankSelect').addEventListener('change', fetchTemplates);
