// Virat Tent House - Main Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // Dynamic WhatsApp button helper
    window.generateWhatsAppLink = function(phone, message) {
        const cleanPhone = phone.replace(/[^0-9]/g, '');
        const encodedMsg = encodeURIComponent(message);
        return `https://wa.me/${cleanPhone}?text=${encodedMsg}`;
    };

    // Client-side quick filter on tables if data-filter-target is present
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(input => {
        const tableId = input.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        if (!table) return;

        input.addEventListener('keyup', () => {
            const query = input.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });
});
