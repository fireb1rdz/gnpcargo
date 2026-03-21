document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    document.querySelectorAll('.menu-item.has-submenu > a')
        .forEach(link => {
            link.addEventListener('click', event => {
                event.preventDefault();

                const current = link.parentElement;

                document.querySelectorAll('.menu-item.has-submenu')
                    .forEach(item => {
                        if (item !== current) {
                            item.classList.remove('active');
                        }
                    });

                current.classList.toggle('active');
            });
        });

    const trigger = document.querySelector('.user-trigger');
    const menu = document.querySelector('.user-menu');

    if (trigger && menu) {
        trigger.addEventListener('click', e => {
            e.stopPropagation();
            menu.classList.toggle('open');
        });

        document.addEventListener('click', () => {
            menu.classList.remove('open');
        });
    }
});
