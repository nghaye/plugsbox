document.addEventListener('DOMContentLoaded', function() {
    const interfaceConfigField = document.getElementById('id_interfaceconfig');
    const ipAddressField = document.getElementById('id_ip_address');
    const ipAddressRow = ipAddressField ? ipAddressField.closest('.field-row, .form-group, .form-field') : null;

    if (!interfaceConfigField || !ipAddressField || !ipAddressRow) {
        return;
    }

    function toggleIpAddressField() {
        const selectedValue = interfaceConfigField.value;
        if (selectedValue === 'static') {
            ipAddressRow.style.display = '';
        } else {
            ipAddressRow.style.display = 'none';
            // Clear the IP address field when hidden
            ipAddressField.value = '';
        }
    }

    // Initial state
    toggleIpAddressField();

    // Listen for changes
    interfaceConfigField.addEventListener('change', toggleIpAddressField);
});