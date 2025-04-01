/**
 * New Customer Accounts Report JavaScript
 * 
 * This file handles the interactive functionality for the New Customer Accounts report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Global variables
let accountTypeChart, dailyAccountsChart;
let dataTable;

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    flatpickr("#moveInDate", {
        dateFormat: "Y-m-d"
    });

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
    if (dataTable) {
        dataTable.destroy();
    }

    dataTable = $('#accountsTable').DataTable({
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
        responsive: true,
        order: [[6, 'desc']], // Sort by Move-In Date, newest first
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    });
}

/**
 * Initialize Account Type Chart
 * @param {Array} data - The account type data to display
 */
function initAccountTypeChart(data) {
    try {
        // Get the canvas element
        const canvas = document.getElementById('accountTypeChart');

        // Check if Chart.js is properly loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded properly');
            showError('Chart.js library failed to load. Please reload the page or check console for details.');
            return;
        }

        // Clear any existing chart
        if (accountTypeChart) {
            accountTypeChart.destroy();
        }

        // Create new chart
        accountTypeChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: data.map(item => item['Account Type'] || 'Unknown'),
                datasets: [{
                    data: data.map(item => item.AccountCount),
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(201, 203, 207, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(201, 203, 207, 1)'
                    ],
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

        // Update summary statistics
        if (data.length > 0) {
            // Find primary account type (most common)
            const primaryType = data[0]['Account Type'] || 'Unknown';
            const primaryCount = data[0].AccountCount;

            $('#primaryAccountType').text(primaryType);
            $('#primaryAccountTypeCount').text(`${primaryCount} accounts`);
        }
    } catch (error) {
        console.error('Error initializing account type chart:', error);
        showError('Failed to initialize account type chart: ' + error.message);
    }
}

/**
 * Initialize Daily Accounts Chart
 * @param {Array} data - The daily accounts data to display
 */
function initDailyAccountsChart(data) {
    try {
        // Get the canvas element
        const canvas = document.getElementById('dailyAccountsChart');

        // Check if Chart.js is properly loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded properly');
            showError('Chart.js library failed to load. Please reload the page or check console for details.');
            return;
        }

        // Clear any existing chart
        if (dailyAccountsChart) {
            dailyAccountsChart.destroy();
        }

        // Format dates for display
        const formattedData = data.map(item => ({
            date: formatDate(item.MoveInDate),
            count: item.NewAccountCount
        }));

        // Create new chart
        dailyAccountsChart = new Chart(canvas, {
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

        // Calculate and update statistics
        if (data.length > 0) {
            // Total accounts
            const totalAccounts = data.reduce((sum, item) => sum + item.NewAccountCount, 0);
            $('#totalAccounts').text(totalAccounts);

            // Daily average
            const dailyAverage = (totalAccounts / data.length).toFixed(1);
            $('#dailyAverage').text(dailyAverage);

            // Date range info
            const startDate = formatDate(data[0].MoveInDate);
            const endDate = formatDate(data[data.length - 1].MoveInDate);
            $('#dateRangeInfo').text(`From ${startDate} to ${endDate}`);
        }
    } catch (error) {
        console.error('Error initializing daily accounts chart:', error);
        showError('Failed to initialize daily accounts chart: ' + error.message);
    }
}

/**
 * Format date for display
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    const moveInDate = $('#moveInDate').val();

    // Build export URL
    let url = '/reports/ssrs/new_customer_accounts/export?';
    if (moveInDate) url += `move_in_date=${moveInDate}`;

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Show an error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    console.error(message);
    alert(message);
}