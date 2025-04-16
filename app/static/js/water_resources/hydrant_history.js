/**
 * Hydrant History Report JavaScript
 * 
 * This file handles the interactive functionality for the Hydrant History report,
 * including loading data, initializing tables, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initial data load
    loadAllData();

    // Set up event listeners for the tabs to load data only when a tab is activated
    $('#dataTabs button').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).data('bs-target');

        if (targetId === '#inspections') {
            // Reload inspections data
            loadInspectionsData();
        } else if (targetId === '#work-orders') {
            // Reload work orders data
            loadWorkOrdersData();
        }
    });

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
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

        // Clear hydrant ID filter
        $('#hydrantId').val('');

        // Reload data with reset filters
        loadAllData();
    });

    $('#exportInspections').click(function () {
        exportInspectionsData();
    });

    $('#exportWorkOrders').click(function () {
        exportWorkOrdersData();
    });
});

/**
 * Load all data for both tabs
 */
function loadAllData() {
    loadInspectionsData();
    loadWorkOrdersData();
}

/**
 * Load hydrant inspections data
 */
function loadInspectionsData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const hydrantId = $('#hydrantId').val();

    // Show loading indicator
    $('#inspectionsTableContainer').addClass('loading');

    // Update filter info text
    updateFilterInfo(hydrantId);

    // Load data from API
    $.ajax({
        url: '/groups/water_resources/hydrant_history/inspections',
        data: {
            start_date: startDate,
            end_date: endDate,
            hydrant_id: hydrantId
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initInspectionsTable(response.data);
                updateInspectionCount(response.data.length);
            } else {
                showError('Error loading inspections data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading inspections data: ' + error);
        },
        complete: function () {
            $('#inspectionsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the inspections data table
 * @param {Array} data - The inspections data
 */
function initInspectionsTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#inspectionsTable')) {
        $('#inspectionsTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#inspectionsTable').DataTable({
        data: data,
        columns: [
            { data: 'INSPECTIONID' },
            { data: 'WORKORDERID' },
            { data: 'INSPTEMPLATENAME' },
            { data: 'ENTITYUID' },
            {
                data: 'INSPDATE',
                render: function (data) {
                    return formatDateSafe(data);
                }
            },
            { data: 'STATUS' }
        ],
        pageLength: 25,
        order: [[4, 'desc']], // Sort by inspection date, newest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Handle window resize
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });

    // Remove loading indicator
    $('#inspectionsTableContainer').removeClass('loading');
}

/**
 * Load hydrant work order data
 */
function loadWorkOrdersData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const hydrantId = $('#hydrantId').val();

    // Show loading indicator
    $('#workOrdersTableContainer').addClass('loading');

    // Update filter info text
    updateFilterInfo(hydrantId);

    // Load data from API
    $.ajax({
        url: '/groups/water_resources/hydrant_history/work-orders',
        data: {
            start_date: startDate,
            end_date: endDate,
            hydrant_id: hydrantId
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initWorkOrdersTable(response.data);
                updateWorkOrderCount(response.data.length);
            } else {
                showError('Error loading work order data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading work order data: ' + error);
        },
        complete: function () {
            $('#workOrdersTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the work orders data table
 * @param {Array} data - The work orders data
 */
function initWorkOrdersTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#workOrdersTable')) {
        $('#workOrdersTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#workOrdersTable').DataTable({
        data: data,
        columns: [
            { data: 'WORKORDERID' },
            { data: 'DESCRIPTION' },
            { data: 'ENTITYUID' },
            {
                data: 'ACTUALFINISHDATE',
                render: function (data) {
                    return formatDateSafe(data);
                }
            },
            { data: 'STATUS' }
        ],
        pageLength: 25,
        order: [[3, 'desc']], // Sort by finish date, newest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Handle window resize
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });

    // Remove loading indicator
    $('#workOrdersTableContainer').removeClass('loading');
}

/**
 * Update inspection count display
 * @param {number} count - The number of inspections
 */
function updateInspectionCount(count) {
    $('#totalInspections').text(count);

    // Update date range info
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    $('#dateRangeInfo').text(`From ${formatDateSafe(startDate)} to ${formatDateSafe(endDate)}`);
}

/**
 * Update work order count display
 * @param {number} count - The number of work orders
 */
function updateWorkOrderCount(count) {
    $('#totalWorkOrders').text(count);
}

/**
 * Update hydrant ID filter info text
 * @param {string} hydrantId - The hydrant ID filter value
 */
function updateFilterInfo(hydrantId) {
    if (hydrantId) {
        $('#hydrantIdInfo').text(`Hydrant ID: ${hydrantId}`);
    } else {
        $('#hydrantIdInfo').text('All hydrants');
    }
}

/**
 * Export inspections data to CSV
 */
function exportInspectionsData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const hydrantId = $('#hydrantId').val();

    // Build export URL
    let url = '/groups/water_resources/hydrant_history/export-inspections';
    let params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (hydrantId) params.push(`hydrant_id=${hydrantId}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Export work orders data to CSV
 */
function exportWorkOrdersData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const hydrantId = $('#hydrantId').val();

    // Build export URL
    let url = '/groups/water_resources/hydrant_history/export-work-orders';
    let params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (hydrantId) params.push(`hydrant_id=${hydrantId}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Format a date string safely without timezone shifting
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDateSafe(dateString) {
    if (!dateString) return '';

    try {
        // Extract date components directly from YYYY-MM-DD format
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);

            // Create date without timezone shifting
            const date = new Date(year, month, day);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                return dateString; // Return original if parsing failed
            }

            // Format using locale-specific date format
            return date.toLocaleDateString();
        }

        // Fallback to original format function if not in expected format
        return formatDate(dateString);
    } catch (error) {
        console.error('Error safely formatting date:', error);
        return dateString;
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
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');

    // Add alert content
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Error:</strong> ${message}
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