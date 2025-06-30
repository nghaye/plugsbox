document.addEventListener('DOMContentLoaded', function() {
    const interfaceConfigField = document.getElementById('id_interfaceconfig');
    const ipAddressField = document.getElementById('id_ip_address');
    const vlanField = document.getElementById('id_vlan');
    const ipAddressRow = ipAddressField ? ipAddressField.closest('.field-row, .form-group, .form-field') : null;
    const vlanRow = vlanField ? vlanField.closest('.field-row, .form-group, .form-field') : null;

    if (!interfaceConfigField) {
        return;
    }

    function toggleFields() {
        const selectedValue = interfaceConfigField.value;
        
        // IP Address field - only visible for 'static'
        if (ipAddressField && ipAddressRow) {
            if (selectedValue === 'static') {
                ipAddressRow.style.display = '';
            } else {
                ipAddressRow.style.display = 'none';
                ipAddressField.value = '';
            }
        }
        
        // VLAN field - visible for 'static' and 'dhcp'
        if (vlanField && vlanRow) {
            if (selectedValue === 'static' || selectedValue === 'dhcp') {
                vlanRow.style.display = '';
            } else {
                vlanRow.style.display = 'none';
                vlanField.value = '';
            }
        }
    }

    // Initial state
    toggleFields();

    // Listen for changes
    interfaceConfigField.addEventListener('change', toggleFields);
});