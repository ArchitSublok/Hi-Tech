document.addEventListener('DOMContentLoaded', function () {
    const target = document.querySelector('.about-image');
    if (!target) return;

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        observer.observe(target);
    } else {
        target.classList.add('is-visible');
    }
});