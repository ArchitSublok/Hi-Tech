document.addEventListener('DOMContentLoaded', function () {
    // Scroll reveal for intro image
    const revealTarget = document.querySelector('.about-image');
    if (revealTarget) {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.2 });
            observer.observe(revealTarget);
        } else {
            revealTarget.classList.add('is-visible');
        }
    }

    // Interactive process showcase
    const stepButtons = document.querySelectorAll('.process-step-btn');
    const processImage = document.getElementById('processImage');

    stepButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (btn.classList.contains('is-active')) return;

            stepButtons.forEach(function (b) {
                b.classList.remove('is-active');
                b.setAttribute('aria-selected', 'false');
            });
            btn.classList.add('is-active');
            btn.setAttribute('aria-selected', 'true');

            const newSrc = btn.getAttribute('data-image');
            if (processImage && newSrc) {
                processImage.classList.add('is-swapping');
                setTimeout(function () {
                    processImage.src = newSrc;
                    processImage.classList.remove('is-swapping');
                }, 250);
            }
        });
    });
});