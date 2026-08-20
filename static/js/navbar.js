document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('primaryNav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', String(open));
    });
});
