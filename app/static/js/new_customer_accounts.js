/**
 * New Customer Accounts Report JavaScript
 * 
 * This file handles the interactive functionality for the New Customer Accounts report,
 * including loading data, initializing charts, and handling user interactions.
 * Updated for compatibility with latest Chart.js v4.x and DataTables 1.13.x
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#moveInDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#moveInDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initial data load
    loadAllData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        const defaultDate = new Date();
        defaultDate.setDate(defaultDate.getDate() - 30);
        const formattedDate = defaultDate.toISOString().slice(0, 10);

        $('#moveInDate').val(formattedDate);
        loadAllData();
    });

    $('#exportData').click(function () {
        exportReportData();
    });
});

/**
 * Load all data for the report
 */
function loadAllData() {
    const moveInDate = $('#moveInDate').val();

    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalAccounts, #dailyAverage, #primaryAccountType').text('-');
    $('#dateRangeInfo, #primaryAccountTypeCount').text('Loading...');

    // Load main data
    $.ajax({
        url: '/reports/ssrs/new_customer_accounts/data',
        data: { move_in_date: moveInDate },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
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

    // Load account type data
    $.ajax({
        url: '/reports/ssrs/new_customer_accounts/account-types',
        data: { move_in_date: moveInDate },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initAccountTypeChart(response.data);
            } else {
                showError('Error loading account type data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading account type data: ' + error);
        }
    });

    // Load daily accounts data
    $.ajax({
        url: '/reports/ssrs/new_customer_accounts/daily-accounts',
        data: { move_in_date: moveInDate },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDailyAccountsChart(response.data);
            } else {
                showError('Error loading daily accounts data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading daily accounts data: ' + error);
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
            { data: 'Account Type' },
            { data: 'LastName' },
            { data: 'FirstName' },
            { data: 'EmailAddress' },
            { data: 'FullAddress' },
            {
                data: 'MoveInDate',
                render: function (data) {
                    return formatDate(data);
                }
            },
            {
                data: 'AccountOpenDate',
                render: function (data) {
                    return formatDate(data);
                }
            }
        ],
        pageLength: 10,
        order: [[6, 'desc']], // Sort by Move-In Date, newest first
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

    // SafeDOM usage for window resize listener
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize Account Type Chart
 * @param {Array} data - The account type data to display
 */
function initAccountTypeChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('accountTypeChart');
    if (!canvas) {
        console.error('Cannot find accountTypeChart canvas element');
        return;
    }

    // Safely destroy existing chart if it exists
    let existingChart;
    try {
        // Chart.js v4.x method
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // Prepare data for the chart
    const labels = data.map(item => item['Account Type'] || 'Unknown');
    const values = data.map(item => item.AccountCount);

    // Create chart colors
    const colors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)'
    ];

    const borderColors = [
        'rgba(54, 162, 235, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(201, 203, 207, 1)'
    ];

    // Create new chart - Updated for Chart.js v4.x
    try {
        // Chart configuration compatible with Chart.js v4.x
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Distribution by Account Type'
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
    } catch (error) {
        console.error('Error creating chart:', error);
        showError('Failed to create chart: ' + error.message);
        return;
    }

    // Update summary statistics
    if (data.length > 0) {
        // Find primary account type (most common)
        data.sort((a, b) => b.AccountCount - a.AccountCount);
        const primaryType = data[0]['Account Type'] || 'Unknown';
        const primaryCount = data[0].AccountCount;
        const total = values.reduce((sum, val) => sum + val, 0);
        const percentage = Math.round((primaryCount / total) * 100);

        $('#primaryAccountType').text(primaryType);
        $('#primaryAccountTypeCount').text(`${primaryCount} accounts (${percentage}%)`);
    }
}

/**
 * Initialize Daily Accounts Chart
 * @param {Array} data - The daily accounts data to display
 */
function initDailyAccountsChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('dailyAccountsChart');
    if (!canvas) {
        console.error('Cannot find dailyAccountsChart canvas element');
        return;
    }

    // Safely destroy existing chart if it exists
    let existingChart;
    try {
        // Chart.js v4.x method
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // Format dates for display
    const formattedData = data.map(item => ({
        date: formatDate(item.MoveInDate),
        count: item.NewAccountCount,
        rawDate: new Date(item.MoveInDate)
    })).sort((a, b) => a.rawDate - b.rawDate);

    // Create new chart - Updated for Chart.js v4.x
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: formattedData.map(item => item.date),
                datasets: [{
                    label: 'New Accounts',
                    data: formattedData.map(item => item.count),
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
                        text: 'Daily New Accounts'
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                return tooltipItems[0].label;
                            },
                            label: function (context) {
                                return `New Accounts: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Accounts'
                        },
                        ticks: {
                            precision: 0
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
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

    // Calculate and update statistics
    if (formattedData.length > 0) {
        // Total accounts
        const totalAccounts = formattedData.reduce((sum, item) => sum + item.count, 0);
        $('#totalAccounts').text(totalAccounts);

        // Daily average
        const dailyAverage = (totalAccounts / formattedData.length).toFixed(1);
        $('#dailyAverage').text(dailyAverage);

        // Date range info
        const startDate = formattedData[0].date;
        const endDate = formattedData[formattedData.length - 1].date;
        $('#dateRangeInfo').text(`From ${startDate} to ${endDate}`);
    }
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
 * Export report data to CSV
 */
function exportReportData() {
    const moveInDate = $('#moveInDate').val();

    // Build export URL
    let url = '/reports/ssrs/new_customer_accounts/export';
    if (moveInDate) {
        url += `?move_in_date=${moveInDate}`;
    }

    // Open in new tab/window
    window.open(url, '_blank');
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