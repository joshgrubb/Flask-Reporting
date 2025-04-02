/**
 * Accounts No Garbage Report JavaScript
 * 
 * This file handles the interactive functionality for the Accounts No Garbage report,
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
    $('#totalAccounts, #totalStreets, #topStreet').text('-');
    $('#topStreetCount').text('Loading...');

    // Load main data
    $.ajax({
        url: '/reports/ssrs/accounts_no_garbage/data',
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

    // Load street summary data
    $.ajax({
        url: '/reports/ssrs/accounts_no_garbage/street-summary',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initStreetChart(response.data);
                updateStreetStats(response.data);
            } else {
                showError('Error loading street data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading street data: ' + error);
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
            { data: 'FirstName' },
            { data: 'FullAddress' },
            { data: 'StreetName' }
        ],
        pageLength: 10,
        order: [[5, 'asc']], // Sort by Street Name
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        rowCallback: function (row, data) {
            // Add classes for styling rows
            $(row).addClass('no-garbage');
        }
    };

    // Initialize DataTable
    const table = $('#accountsTable').DataTable(dataTableOptions);

    // Resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize Street Chart
 * @param {Array} data - The street data to display
 */
function initStreetChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('streetChart');
    if (!canvas) {
        console.error('Cannot find streetChart canvas element');
        return;
    }

    // Safely destroy existing chart if it exists
    if (window.streetChart) {
        if (typeof window.streetChart.destroy === 'function') {
            window.streetChart.destroy();
        } else {
            window.streetChart = null;
        }
    }

    // Check if there's a Chart instance attached to the canvas
    const chartInstance = Chart.getChart(canvas);
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Limit to top 10 streets
    const topData = data.slice(0, 10);

    // Prepare data for the chart
    const labels = topData.map(item => item.StreetName || 'Unknown');
    const values = topData.map(item => item.AccountCount);

    // Create chart colors
    const backgroundColor = 'rgba(54, 162, 235, 0.7)';
    const borderColor = 'rgba(54, 162, 235, 1)';

    // Create new chart
    try {
        window.streetChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Accounts',
                    data: values,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bar chart
                plugins: {
                    title: {
                        display: true,
                        text: 'Top 10 Streets Without Garbage Service'
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
                    y: {
                        title: {
                            display: true,
                            text: 'Street Name'
                        }
                    },
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Accounts'
                        },
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating chart:', error);
        showError('Failed to create chart: ' + error.message);
        return;
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
 * Update street statistics
 * @param {Array} data - The street data
 */
function updateStreetStats(data) {
    if (data && data.length > 0) {
        // Update total streets
        $('#totalStreets').text(data.length);

        // Update top street info
        const topStreet = data[0];
        $('#topStreet').text(topStreet.StreetName || 'Unknown');
        $('#topStreetCount').text(`${topStreet.AccountCount} accounts`);
    }
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Open in new tab/window
    window.open('/reports/ssrs/accounts_no_garbage/export', '_blank');
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