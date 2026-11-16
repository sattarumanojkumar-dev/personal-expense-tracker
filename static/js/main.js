/**
 * Personal Expense Tracker - Interactive UI Scripts
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const appSidebar = document.getElementById('appSidebar');

    if (sidebarToggle && appSidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            appSidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (e) {
            if (window.innerWidth < 992 && appSidebar.classList.contains('show')) {
                if (!appSidebar.contains(e.target) && e.target !== sidebarToggle) {
                    appSidebar.classList.remove('show');
                }
            }
        });
    }

    // 2. Auto-dismiss Bootstrap Alerts after 5 seconds
    const alerts = document.querySelectorAll('.messages-container .alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});
