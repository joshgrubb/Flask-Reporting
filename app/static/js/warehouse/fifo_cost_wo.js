/**
 * FIFO Work Order Cost Report JavaScript
 * 
 * This file handles the interactive functionality for the FIFO Work Order Cost report,
 * including loading data, initializing tables, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker if available
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });

        // Set default dates
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 30); // Default to last 30 days
        const formattedStartDate = startDate.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(endDate);
    }

    // Initial data load - this is commented out for now as the endpoint is not fully implemented
    // loadWorkOrderData();

    // Event handlers
    $('#applyFilters').click(function () {
        // Placeholder - this will be implemented when the backend is ready
        showError('This report is not yet fully implemented');
    });

    $('#resetFilters').click(function () {
        // Reset to default dates (last 30 days)
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 30);
        const formattedStartDate = startDate.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(endDate);
    });

    $('#exportData').click(function () {
        // Placeholder - this will be implemented when the backend is ready
        showError('Export functionality is not yet implemented');
    });
});

/**
 * Load work order data based on filters
 */
function loadWorkOrderData() {
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalWorkOrders, #totalCost, #averageCost').text('-');
    $('#dateRangeInfo').text('Loading...');

    // Placeholder for AJAX call
    // This is a placeholder and will be implemented when the backend is ready
    setTimeout(function () {
        // Remove loading state
        $('#dataTableContainer').removeClass('loading');

        // Update stats with placeholder data
        $('#totalWorkOrders').text('0');
        $('#totalCost').text('$0.00');
        $('#averageCost').text('$0.00');
        $('#dateRangeInfo').text(`${formatDate(startDate)} to ${formatDate(endDate)}`);

        showError('This report is not yet fully implemented');
    }, 1000);
}

/**
 * Format date for display
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);

        // Check if the date is valid
        if (isNaN(date.getTime())) {
            return '';
        }

        return date.toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
}

/**
 * Show an error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    console.error(message);

    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-warning alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');

    // Add alert content
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Notice:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Find a place to add the alert
    const container = document.querySelector('.container');
    if (container) {
        // Add to beginning of container
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        // If no container found, add to body
        document.body.insertBefore(alertDiv, document.body.firstChild);
    }

    // Auto-close after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 150);
    }, 5000);
}