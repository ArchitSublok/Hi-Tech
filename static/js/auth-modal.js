document.addEventListener('DOMContentLoaded', function () {
    var overlay = document.getElementById('authModalOverlay');
    if (!overlay) return;
    var closeButton = document.getElementById('authModalClose');
    var triggers = document.querySelectorAll('.auth-trigger-btn');
    var tabs = document.querySelectorAll('.modal-tab');
    var forms = { login: document.getElementById('loginForm'), signup: document.getElementById('signupForm') };

    function showTab(name) {
        tabs.forEach(function (tab) { tab.classList.toggle('is-active', tab.dataset.tab === name); });
        Object.keys(forms).forEach(function (key) { forms[key].hidden = key !== name; });
    }
    function openModal() { overlay.hidden = false; document.body.style.overflow = 'hidden'; (forms.login.querySelector('input') || forms.login).focus(); }
    function closeModal() { overlay.hidden = true; document.body.style.overflow = ''; }
    triggers.forEach(function (trigger) { trigger.addEventListener('click', function () { showTab('login'); openModal(); }); });
    closeButton.addEventListener('click', closeModal);
    overlay.addEventListener('click', function (event) { if (event.target === overlay) closeModal(); });
    document.addEventListener('keydown', function (event) { if (event.key === 'Escape' && !overlay.hidden) closeModal(); });
    tabs.forEach(function (tab) { tab.addEventListener('click', function () { showTab(tab.dataset.tab); }); });

    function setErrors(form, errors) {
        form.querySelectorAll('.field-error, .modal-error').forEach(function (element) { element.textContent = ''; });
        Object.keys(errors || {}).forEach(function (name) {
            var element = form.querySelector('[data-error-for="' + name + '"]');
            if (element) element.textContent = Array.isArray(errors[name]) ? errors[name].join(' ') : errors[name];
        });
    }
    Object.keys(forms).forEach(function (kind) {
        forms[kind].addEventListener('submit', function (event) {
            event.preventDefault();
            var form = forms[kind]; var button = form.querySelector('button[type=submit]');
            setErrors(form, {}); button.disabled = true; button.textContent = kind === 'login' ? 'Signing in...' : 'Creating account...';
            fetch('/accounts/api/' + kind + '/', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
                body: new FormData(form)
            })
                .then(function (response) {
                    return response.json()
                        .then(function (data) { return { ok: response.ok, data: data }; })
                        .catch(function () {
                            return { ok: false, data: { errors: { '__all__': ['The server rejected the request. Refresh the page and try again.'] } } };
                        });
                })
                .then(function (result) { if (result.ok && result.data.success) window.location.reload(); else setErrors(form, result.data.errors || { '__all__': ['Please try again.'] }); })
                .catch(function () { setErrors(form, { '__all__': ['We could not complete that request. Please try again.'] }); })
                .finally(function () { button.disabled = false; button.textContent = kind === 'login' ? 'Log in' : 'Create account'; });
        });
    });
});
