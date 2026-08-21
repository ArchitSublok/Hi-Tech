document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('primaryNav');
    if (!toggle || !nav) return;

    function closeMenu() {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', function (event) {
        if (!nav.classList.contains('is-open')) return;
        if (nav.contains(event.target) || toggle.contains(event.target)) return;
        closeMenu();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && nav.classList.contains('is-open')) closeMenu();
    });
});
