/**
 * VFLEX Report JavaScript
 * 
 * This file handles the interactive functionality for the VFLEX report,
 * including data loading, pagination, and export functionality.
 */

// Current pagination state
let currentPage = 1;
let totalPages = 1;
let pageSize = 50;

// Document ready function
$(document).ready(function () {
    // Load initial data
    loadVflexData(currentPage);
    loadExecutionLogs();

    // Event handlers
    $('#refreshData').click(function () {
        loadVflexData(currentPage);
    });

    $('#exportCSV').click(function () {
        exportVflexData('csv');
    });

    $('#exportFixed').click(function () {
        exportVflexData('fixed');
    });

    $('#prevPage').click(function () {
        if (currentPage > 1) {
            currentPage--;
            loadVflexData(currentPage);
        }
    });

    $('#nextPage').click(function () {
        if (currentPage < totalPages) {
            currentPage++;
            loadVflexData(currentPage);
        }
    });
});

/**
 * Load VFLEX data with pagination
 * @param {number} page - The page number to load
 */
function loadVflexData(page) {
    // Show loading indicator
    $('#dataTableContainer').addClass('loading');
    $('#totalRecordsInfo').text('Loading...');

    // Fetch data from server
    $.ajax({
        url: '/groups/utilities_billing/vflex/data',
        data: {
            page: page,
            limit: pageSize
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Update pagination state
                currentPage = response.page;
                totalPages = response.pages;

                // Initialize DataTable with the data
                initDataTable(response.data);

                // Update pagination controls
                updatePaginationControls();

                // Update info text
                const startRecord = ((currentPage - 1) * pageSize) + 1;
                const endRecord = Math.min(startRecord + response.data.length - 1, response.total);
                $('#totalRecordsInfo').text(`Showing ${startRecord} to ${endRecord} of ${response.total} records`);

                // Also update the stats card
                $('#totalRecords').text(response.total);
            } else {
                showError('Error loading data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading data: ' + error);
        },
        complete: function () {
            $('#dataTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the data table
 * @param {Array} data - The data to display in the table
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#vflexTable')) {
        $('#vflexTable').DataTable().destroy();
    }

    // Empty the table body
    $('#vflexTable tbody').empty();

    // Add rows to the table
    data.forEach(function (row) {
        const tableRow = `
            <tr>
                <td>${escapeHtml(row.MeterID || '')}</td>
                <td>${escapeHtml(row.RadioID || '')}</td>
                <td>${escapeHtml(row.DeviceStatus || '')}</td>
                <td>${escapeHtml(row.AccountID || '')}</td>
                <td>${escapeHtml(row.CustomerName || '')}</td>
                <td>${escapeHtml(row.StreetAddress || '')}</td>
                <td>${escapeHtml(row.City || '')}</td>
                <td>${escapeHtml(row.State || '')}</td>
                <td>${escapeHtml(row.ZipCode || '')}</td>
                <td>${escapeHtml(row.PhoneNumber || '')}</td>
            </tr>
        `;
        $('#vflexTable tbody').append(tableRow);
    });

    // Initialize DataTable
    $('#vflexTable').DataTable({
        searching: true,
        ordering: true,
        paging: false, // We handle pagination separately
        info: false,
        scrollX: true,
        language: {
            search: "Filter table:"
        }
    });
}

/**
 * Update the pagination controls based on current state
 */
function updatePaginationControls() {
    // Update pagination info text
    $('#paginationInfo').text(`Page ${currentPage} of ${totalPages}`);

    // Update previous button state
    $('#prevPage').prop('disabled', currentPage <= 1);

    // Update next button state
    $('#nextPage').prop('disabled', currentPage >= totalPages);
}

/**
 * Load execution logs for the VFLEX process
 */
function loadExecutionLogs() {
    // Show loading indicator
    $('#logsTableContainer').addClass('loading');

    // Fetch log data from server
    $.ajax({
        url: '/groups/utilities_billing/vflex/logs',
        data: {
            limit: 100 // Get the most recent 100 log entries
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initLogsTable(response.data);
            } else {
                showError('Error loading logs: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading logs: ' + error);
        },
        complete: function () {
            $('#logsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the logs table
 * @param {Array} data - The log data to display
 */
function initLogsTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#logsTable')) {
        $('#logsTable').DataTable().destroy();
    }

    // Empty the table body
    $('#logsTable tbody').empty();

    // Add rows to the table
    data.forEach(function (row) {
        // Format timestamp
        const timestamp = row.LogTimestamp ? formatDateTime(row.LogTimestamp) : '';

        // Format error message - truncate if too long
        let errorMessage = row.ErrorMessage || '';
        if (errorMessage.length > 100) {
            errorMessage = errorMessage.substring(0, 100) + '...';
        }

        // Row class based on status
        const rowClass = row.Status === 'Success' ? 'success-row' : 'error-row';

        const tableRow = `
            <tr class="${rowClass}">
                <td>${timestamp}</td>
                <td>
                    <span class="badge ${row.Status === 'Success' ? 'bg-success' : 'bg-danger'}">
                        ${escapeHtml(row.Status || '')}
                    </span>
                </td>
                <td>${escapeHtml(row.ExecutionSeconds || '')}</td>
                <td>${escapeHtml(errorMessage)}</td>
                <td>${escapeHtml(row.ErrorSeverity || '')}</td>
                <td>${escapeHtml(row.ErrorState || '')}</td>
                <td>${escapeHtml(row.ErrorProcedure || '')}</td>
            </tr>
        `;
        $('#logsTable tbody').append(tableRow);
    });

    // Initialize DataTable
    $('#logsTable').DataTable({
        searching: true,
        ordering: true,
        order: [[0, 'desc']], // Sort by timestamp, newest first
        paging: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100],
        scrollX: true,
        language: {
            search: "Filter:"
        }
    });
}

/**
 * Export VFLEX data
 * @param {string} format - The export format ('csv' or 'fixed')
 */
function exportVflexData(format) {
    // Show alert that this may take some time
    showAlert('Generating export file. This may take a few moments...', 'info');

    // Set the export URL based on format
    let exportUrl = '';
    if (format === 'csv') {
        exportUrl = '/groups/utilities_billing/vflex/export';
    } else {
        exportUrl = '/groups/utilities_billing/vflex/export-fixed';
    }

    // Open the export URL in a new tab
    window.open(exportUrl, '_blank');
}

/**
 * Format a datetime string safely without timezone shifting
 * @param {string} dateTimeString - The datetime string to format (e.g., "2025-04-01 14:30:00")
 * @param {boolean} includeTime - Whether to include time in the formatted output (default: true)
 * @returns {string} - Formatted datetime string
 */
function formatDateTime(dateTimeString, includeTime = true) {
    if (!dateTimeString) return '';

    try {
        // Extract date and time components directly from string
        // Match format like "2025-04-01 14:30:00" or "2025-04-01T14:30:00"
        const match = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})/);

        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);
            const hours = parseInt(match[4], 10);
            const minutes = parseInt(match[5], 10);
            const seconds = parseInt(match[6], 10);

            // Create date without timezone shifting by specifying all components
            const date = new Date(year, month, day, hours, minutes, seconds);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                console.warn('Invalid date created from:', dateTimeString);
                return dateTimeString; // Return original if parsing failed
            }

            // Format options
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            // Add time options if requested
            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true; // Use 12-hour format (AM/PM)
            }

            // Format using locale-specific datetime format
            return date.toLocaleString(undefined, options);
        }

        // Check for date-only format (YYYY-MM-DD)
        const dateOnlyMatch = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (dateOnlyMatch) {
            const year = parseInt(dateOnlyMatch[1], 10);
            const month = parseInt(dateOnlyMatch[2], 10) - 1;
            const day = parseInt(dateOnlyMatch[3], 10);

            const date = new Date(year, month, day);

            if (isNaN(date.getTime())) {
                return dateTimeString;
            }

            return date.toLocaleDateString();
        }

        // If no pattern matches, try direct parsing as fallback
        // (but this may cause timezone shifts)
        const directDate = new Date(dateTimeString);
        if (!isNaN(directDate.getTime())) {
            console.warn('Using direct date parsing which may cause timezone shifts:', dateTimeString);

            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true;
            }

            return directDate.toLocaleString(undefined, options);
        }

        // Return original string if all parsing attempts fail
        return dateTimeString;
    } catch (error) {
        console.error('Error formatting datetime:', error);
        return dateTimeString;
    }
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';

    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type ('success', 'info', 'warning', 'danger')
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');

    // Add alert content
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'info' ? 'info-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
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

/**
 * Show an error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    console.error(message);
    showAlert(message, 'danger');
}