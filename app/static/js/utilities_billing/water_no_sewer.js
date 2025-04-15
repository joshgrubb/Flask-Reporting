/**
 * Water No Sewer Report JavaScript
 * 
 * This file handles the interactive functionality for the Water No Sewer report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initial data load
    loadAllData();

    // Event handlers
    $('#exportData').click(function () {
        exportReportData();
    });
});

/**
 * Load all data for the report
 */
function loadAllData() {
    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalAccounts').text('-');

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/water_no_sewer/data',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                updateAccountStats(response.data);
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

    // Load account type summary data
    $.ajax({
        url: '/groups/utilities_billing/water_no_sewer/summary',
        dataType: 'json',
        success: function (response) {
            console.log('Summary response:', response);
            if (response.success && response.data && response.data.length > 0) {
                initAccountTypeChart(response.data);
            } else {
                console.error('No summary data available:', response);
                // Show a message in the chart container
                const chartCanvas = document.getElementById('accountTypeChart');
                if (chartCanvas) {
                    const parent = chartCanvas.parentElement;
                    parent.innerHTML = '<div class="alert alert-info">No account type data available.</div>';
                }
            }
        },
        error: function (xhr, status, error) {
            console.error('Error loading summary data:', error);
            showError('Error loading summary data: ' + error);
        }
    });
}

/**
 * Initialize DataTable with account data
 * @param {Array} data - The account data to display
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#accountsTable')) {
        $('#accountsTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'FullAccountNumber' },
            { data: 'AccountType' },
            { data: 'LastName' },
            { data: 'FirstName' }
        ],
        pageLength: 25,
        order: [[0, 'desc']], // Sort by Account Number, newest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#accountsTable').DataTable(dataTableOptions);

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize Account Type Chart
 * @param {Array} data - The account type summary data
 */
function initAccountTypeChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Add debugging to check the data
    console.log('Account type data:', data);

    // Check if data is valid
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.error('Invalid or empty data for account type chart');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('accountTypeChart');
    if (!canvas) {
        console.error('Cannot find accountTypeChart canvas element');
        return;
    }

    // Safely destroy existing chart if it exists
    try {
        const chartInstance = Chart.getChart(canvas);
        if (chartInstance) {
            chartInstance.destroy();
        }
    } catch (e) {
        console.warn('Error checking for existing chart:', e);
    }

    // Prepare data for chart
    const labels = data.map(item => item.AccountType || 'Unknown');
    const values = data.map(item => parseInt(item.AccountCount) || 0); // Ensure numbers

    // Debug the prepared data
    console.log('Chart labels:', labels);
    console.log('Chart values:', values);

    // Create color palette
    const colors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
    ];

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';

    // Create new chart with try-catch
    try {
        const chart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, values.length),
                    borderColor: colors.map(color => color.replace('0.7', '1')).slice(0, values.length),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: textColor
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        console.log('Chart successfully created:', chart);
    } catch (error) {
        console.error('Error creating chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Update account statistics
 * @param {Array} data - The account data
 */
function updateAccountStats(data) {
    if (data && data.length > 0) {
        // Update total accounts
        $('#totalAccounts').text(data.length);
    }
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Open in new tab/window
    window.open('/groups/utilities_billing/water_no_sewer/export', '_blank');
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