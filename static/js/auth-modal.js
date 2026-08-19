document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('authModalOverlay');
    if (!overlay) return;

    const openBtn = document.getElementById('authTriggerBtn');
    const closeBtn = document.getElementById('authModalClose');
    const tabLogin = document.getElementById('tabLogin');
    const tabSignup = document.getElementById('tabSignup');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    function openModal(tab) {
        overlay.hidden = false;
        switchTab(tab || 'login');
    }

    function closeModal() {
        overlay.hidden = true;
        clearErrors(loginForm);
        clearErrors(signupForm);
    }

    function switchTab(tab) {
        const isLogin = tab === 'login';
        loginForm.hidden = !isLogin;
        signupForm.hidden = isLogin;
        tabLogin.classList.toggle('is-active', isLogin);
        tabSignup.classList.toggle('is-active', !isLogin);
    }

    if (openBtn) openBtn.addEventListener('click', function () { openModal('login'); });
    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !overlay.hidden) closeModal();
    });

    tabLogin.addEventListener('click', function () { switchTab('login'); });
    tabSignup.addEventListener('click', function () { switchTab('signup'); });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function clearErrors(form) {
        form.querySelectorAll('.field-error, .modal-error').forEach(function (el) { el.textContent = ''; });
    }

    function showErrors(form, errors) {
        clearErrors(form);
        Object.keys(errors).forEach(function (field) {
            const target = form.querySelector(`[data-error-for="${field}"]`);
            const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
            const text = typeof message === 'object' ? (message.message || 'Invalid value.') : message;
            if (target) {
                target.textContent = text;
            } else {
                const general = form.querySelector('[data-error-for="__all__"]');
                if (general) general.textContent = text;
            }
        });
    }

    async function submitForm(form, url, submitBtnId, onSuccess) {
        const submitBtn = document.getElementById(submitBtnId);
        clearErrors(form);

        const formData = new FormData(form);
        const payload = {};
        formData.forEach(function (value, key) { payload[key] = value; });

        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Please wait...';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                onSuccess(data);
            } else {
                showErrors(form, data.errors || { __all__: ['Something went wrong. Please try again.'] });
            }
        } catch (err) {
            showErrors(form, { __all__: ['Network error. Please try again.'] });
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        submitForm(loginForm, '/accounts/api/login/', 'loginSubmitBtn', function () {
            window.location.reload();
        });
    });

    signupForm.addEventListener('submit', function (e) {
        e.preventDefault();
        submitForm(signupForm, '/accounts/api/signup/', 'signupSubmitBtn', function () {
            window.location.reload();
        });
    });
});