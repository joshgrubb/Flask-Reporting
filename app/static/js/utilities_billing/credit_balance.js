/**
 * Credit Balance Report JavaScript
 * 
 * This file handles the interactive functionality for the Credit Balance report,
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
    $('#totalAccounts, #totalCredit, #avgCredit, #maxCredit').text('-');

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/credit_balance/data',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                initCreditDistributionChart(response.data);
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

    // Load summary data
    $.ajax({
        url: '/groups/utilities_billing/credit_balance/summary',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                updateSummaryStats(response.data);
            } else {
                showError('Error loading summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
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
            {
                data: 'LastBalance',
                render: function (data) {
                    // Format balance as negative currency (red)
                    return `<span class="text-danger">${formatCurrency(data)}</span>`;
                }
            },
            { data: 'FormalName' },
            { data: 'FullAddress' },
            { data: 'EmailAddress' },
            {
                data: 'MoveOutDate',
                render: function (data) {
                    return formatDate(data);
                }
            },
            {
                // Combine phone numbers
                data: null,
                render: function (data, type, row) {
                    let phones = [];
                    if (row.CellPhone) phones.push(`Cell: ${row.CellPhone}`);
                    if (row.PrimaryPhone) phones.push(`Primary: ${row.PrimaryPhone}`);
                    return phones.join('<br>');
                }
            },
            {
                data: 'AccountStatus',
                render: function (data) {
                    // Format status with badge
                    const statusClass = data === 'Active' ? 'bg-success' : 'bg-secondary';
                    return `<span class="badge ${statusClass}">${data}</span>`;
                }
            }
        ],
        pageLength: 25,
        order: [[1, 'asc']], // Sort by balance amount, most negative first
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
 * Initialize Credit Distribution Chart
 * @param {Array} data - The account data
 */
function initCreditDistributionChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('creditDistributionChart');
    if (!canvas) {
        console.error('Cannot find creditDistributionChart canvas element');
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

    // Calculate distribution data
    const buckets = calculateCreditDistribution(data);

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Create new chart
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: buckets.labels,
                datasets: [{
                    label: 'Number of Accounts',
                    data: buckets.counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Credit Balance Distribution',
                        color: textColor,
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                return tooltipItems[0].label;
                            },
                            label: function (context) {
                                return `Accounts: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Credit Amount ($)',
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Number of Accounts',
                            color: textColor
                        },
                        beginAtZero: true,
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            precision: 0,
                            color: textColor
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Calculate distribution data for credit amounts
 * @param {Array} data - The account data
 * @returns {Object} - Object with labels and counts arrays
 */
function calculateCreditDistribution(data) {
    // Define credit balance ranges
    const ranges = [
        { max: -10, label: '$0-$10' },
        { max: -25, label: '$10-$25' },
        { max: -50, label: '$25-$50' },
        { max: -100, label: '$50-$100' },
        { max: -250, label: '$100-$250' },
        { max: -500, label: '$250-$500' },
        { max: -1000, label: '$500-$1000' },
        { max: -Infinity, label: '$1000+' }
    ];

    // Initialize counts for each range
    const counts = Array(ranges.length).fill(0);

    // Count accounts in each range
    data.forEach(account => {
        const balance = account.LastBalance;
        // Skip if balance is positive or missing
        if (!balance || balance >= 0) return;

        // Find appropriate range
        const absBalance = Math.abs(balance);
        let rangeIndex = ranges.findIndex(range => absBalance <= Math.abs(range.max));

        // Use last bucket if no range found
        if (rangeIndex === -1) rangeIndex = ranges.length - 1;

        // Increment count for this range
        counts[rangeIndex]++;
    });

    return {
        labels: ranges.map(r => r.label),
        counts: counts
    };
}

/**
 * Update summary statistics
 * @param {Object} data - The summary data
 */
function updateSummaryStats(data) {
    if (!data) return;

    // Update total accounts
    $('#totalAccounts').text(data.TotalAccounts || 0);

    // Update total credit amount
    $('#totalCredit').text(formatCurrency(data.TotalCreditAmount || 0));

    // Update average credit amount
    $('#avgCredit').text(formatCurrency(data.AvgCreditAmount || 0));

    // Update maximum credit amount
    $('#maxCredit').text(formatCurrency(data.MaxCreditAmount || 0));
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Build export URL
    const url = '/groups/utilities_billing/credit_balance/export';

    // Open in new tab/window
    window.open(url, '_blank');
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
 * Format a number as currency
 * @param {number|string} value - The number to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value) {
    if (value == null) return '$0.00';

    try {
        // Parse the value to make sure it's a number
        const numValue = parseFloat(value);

        if (isNaN(numValue)) return '$0.00';

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(numValue);
    } catch (error) {
        console.error('Error formatting currency:', error);
        return '$0.00';
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