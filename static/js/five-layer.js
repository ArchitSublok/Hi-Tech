document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.layer-tab');
    const panels = document.querySelectorAll('.layer-panel');

    if (!tabs.length || !panels.length) return;

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            const target = tab.getAttribute('data-layer');

            tabs.forEach(function (t) {
                t.classList.remove('is-active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('is-active');
            tab.setAttribute('aria-selected', 'true');

            panels.forEach(function (panel) {
                panel.classList.toggle('is-active', panel.getAttribute('data-layer-panel') === target);
            });
        });
    });
});
