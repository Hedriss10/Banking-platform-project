function toggleTables(convenioId) {
    var element = document.getElementById("tables-" + convenioId);
    var isVisible = element.style.display !== "none";
    element.style.display = isVisible ? "none" : "block";
}
