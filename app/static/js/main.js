// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Add fade-in animation to elements
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.card, .stat-card').forEach(el => {
    observer.observe(el);
});

// Loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-overlay';
    spinner.innerHTML = '<div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.remove();
    }
}
