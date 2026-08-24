document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('filterToggle');
    const filters = document.getElementById('collectionFilters');

    if (toggleBtn && filters) {
        toggleBtn.addEventListener('click', function () {
            var open = filters.classList.toggle('is-open');
            toggleBtn.setAttribute('aria-expanded', String(open));
        });
    }
});
