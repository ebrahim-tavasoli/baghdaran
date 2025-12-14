(function($) {
    $(document).ready(function() {
        // Function to toggle driver field based on water_source_type
        function toggleDriverField() {
            var waterSourceType = $('#id_water_source_type').val();
            var driverField = $('.field-driver');
            var driverInput = $('#id_driver');
            
            if (waterSourceType === 'time') {
                // Disable and hide driver field when water_source_type is "time"
                driverInput.prop('disabled', true);
                driverInput.val('');  // Clear the selection
                driverField.hide();
            } else {
                // Enable and show driver field for other cases
                driverInput.prop('disabled', false);
                driverField.show();
            }
        }
        
        // Run on page load
        toggleDriverField();
        
        // Run when water_source_type changes
        $('#id_water_source_type').change(function() {
            toggleDriverField();
        });
    });
})(django.jQuery);
