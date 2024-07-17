document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('proposalTableContainer');

    function loadTableData(pageUrl) {
        fetch(pageUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html;
                attachEventToPaginationLinks();
            })
            .catch(error => console.error('Error loading the data:', error));
    }

    function attachEventToPaginationLinks() {
        document.querySelectorAll('#proposalTableContainer .pagination a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                loadTableData(this.href);
            });
        });
    }

    attachEventToPaginationLinks();
});