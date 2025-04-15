/**
 * Warehouse Audit Transactions Report JavaScript
 * 
 * This file handles the interactive functionality for the Warehouse Audit Transactions report,
 * including loading data, initializing charts and tables, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initialize tabs if they exist
    const tabElements = document.querySelectorAll('#dataTabs button');
    if (tabElements.length > 0) {
        tabElements.forEach(tab => {
            tab.addEventListener('click', function (e) {
                e.preventDefault();
                $(this).tab('show');
            });
        });
    }

    // Set up event listeners for the tabs to load data only when a tab is activated
    $('#dataTabs button').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).data('bs-target');

        if (targetId === '#accounts' && !window.accountsDataLoaded) {
            loadAccountSummary();
        } else if (targetId === '#materials' && !window.materialsDataLoaded) {
            loadMaterialSummary();
        }
    });

    // Initial data load for main transactions tab
    loadTransactionsData();

    // Event handlers
    $('#applyFilters').click(function () {
        // Reset data loaded flags when filters are applied
        window.accountsDataLoaded = false;
        window.materialsDataLoaded = false;

        // Load data for the active tab
        const activeTab = $('#dataTabs button.active').data('bs-target');

        if (activeTab === '#transactions') {
            loadTransactionsData();
        } else if (activeTab === '#accounts') {
            loadAccountSummary();
        } else if (activeTab === '#materials') {
            loadMaterialSummary();
        }
    });

    $('#resetFilters').click(function () {
        // Reset to default dates (previous month)
        resetDateFilters();

        // Clear other filter fields
        $('#accountNumber, #materialId').val('');

        // Reset data loaded flags
        window.accountsDataLoaded = false;
        window.materialsDataLoaded = false;

        // Load data for the active tab
        const activeTab = $('#dataTabs button.active').data('bs-target');

        if (activeTab === '#transactions') {
            loadTransactionsData();
        } else if (activeTab === '#accounts') {
            loadAccountSummary();
        } else if (activeTab === '#materials') {
            loadMaterialSummary();
        }
    });

    $('#exportData').click(function () {
        exportReportData();
    });
});

/**
 * Reset date filters to the first and last day of the previous month
 */
function resetDateFilters() {
    const today = new Date();

    // First day of current month
    const firstDayCurrentMonth = new Date(today.getFullYear(), today.getMonth(), 1);

    // Last day of previous month
    const lastDayPrevMonth = new Date(firstDayCurrentMonth);
    lastDayPrevMonth.setDate(lastDayPrevMonth.getDate() - 1);

    // First day of previous month
    const firstDayPrevMonth = new Date(lastDayPrevMonth.getFullYear(), lastDayPrevMonth.getMonth(), 1);

    // Format dates for input fields
    const formattedStartDate = firstDayPrevMonth.toISOString().slice(0, 10);
    const formattedEndDate = lastDayPrevMonth.toISOString().slice(0, 10);

    // Set input values
    $('#startDate').val(formattedStartDate);
    $('#endDate').val(formattedEndDate);
}

/**
 * Load transactions data based on filters
 */
function loadTransactionsData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const accountNumber = $('#accountNumber').val();
    const materialId = $('#materialId').val();

    // Show loading indicators
    $('#transactionsTableContainer').addClass('loading');
    $('#totalTransactions, #totalCostChange, #uniqueMaterials').text('-');
    $('#dateRangeInfo').text('Loading...');

    // Load data from API
    $.ajax({
        url: '/groups/warehouse/audit_transactions/data',
        data: {
            start_date: startDate,
            end_date: endDate,
            account_number: accountNumber,
            material_id: materialId
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initTransactionsTable(response.data);
                updateStats(response.data);

                // Also load account and material summaries for charts
                loadChartData();
            } else {
                showError('Error loading data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading data: ' + error);
        },
        complete: function () {
            $('#transactionsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the transactions DataTable
 * @param {Array} data - The transaction data
 */
function initTransactionsTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#transactionsTable')) {
        $('#transactionsTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#transactionsTable').DataTable({
        data: data,
        columns: [
            // { data: 'TRANSACTIONID' },
            {
                data: 'TRANSDATETIME',
                render: function (data) {
                    return formatDateTime(data);
                }
            },
            { data: 'TRANSTYPE' },
            { data: 'PERSONNEL' },
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            {
                data: 'OLDQUANT',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                data: 'NEWQUANT',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                data: 'OLDUNITCOST',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'NEWUNITCOST',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            { data: 'ACCTNUM' },
            {
                data: 'COSTDIFF',
                render: function (data) {
                    // Color negative values red, positive green
                    const value = parseFloat(data);
                    const formattedValue = formatCurrency(value);

                    if (value < 0) {
                        return '<span class="text-danger">' + formattedValue + '</span>';
                    } else if (value > 0) {
                        return '<span class="text-success">' + formattedValue + '</span>';
                    }
                    return formattedValue;
                }
            },
            {
                // Use either ISSUE or RECEIVE work order ID, whichever is available
                data: null,
                render: function (data) {
                    return data.ISSUE_WORKORDERID || data.RECEIVE_WORKORDERID || '';
                }
            }
        ],
        pageLength: 25,
        order: [[1, 'desc']], // Sort by date, newest first
        scrollX: true,
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Load account summary data
 */
function loadAccountSummary() {
    // Get filter values - only use date range for summary data
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicator
    $('#accountsTableContainer').addClass('loading');

    // Load data from API
    $.ajax({
        url: '/groups/warehouse/audit_transactions/account-summary',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initAccountsTable(response.data);
                window.accountsDataLoaded = true;
            } else {
                showError('Error loading account summary: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading account summary: ' + error);
        },
        complete: function () {
            $('#accountsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the accounts summary DataTable
 * @param {Array} data - The account summary data
 */
function initAccountsTable(data) {
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

    // Initialize DataTable
    const table = $('#accountsTable').DataTable({
        data: data,
        columns: [
            { data: 'ACCTNUM' },
            { data: 'TransactionCount' },
            { data: 'MaterialCount' },
            {
                data: 'TotalCostDiff',
                render: function (data) {
                    return formatCurrency(data);
                }
            }
        ],
        pageLength: 25,
        order: [[3, 'desc']], // Sort by total cost difference, largest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Load material summary data
 */
function loadMaterialSummary() {
    // Get filter values - only use date range for summary data
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicator
    $('#materialsTableContainer').addClass('loading');

    // Load data from API
    $.ajax({
        url: '/groups/warehouse/audit_transactions/material-summary',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initMaterialsTable(response.data);
                window.materialsDataLoaded = true;
            } else {
                showError('Error loading material summary: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading material summary: ' + error);
        },
        complete: function () {
            $('#materialsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the materials summary DataTable
 * @param {Array} data - The material summary data
 */
function initMaterialsTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#materialsTable')) {
        $('#materialsTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#materialsTable').DataTable({
        data: data,
        columns: [
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            { data: 'TransactionCount' },
            {
                data: 'TotalCostDiff',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'MinOldCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'MaxNewCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'AvgNewCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            }
        ],
        pageLength: 25,
        order: [[3, 'desc']], // Sort by total cost difference, largest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Load chart data for the account and material charts
 */
function loadChartData() {
    // Load account summary data for chart
    $.ajax({
        url: '/groups/warehouse/audit_transactions/account-summary',
        data: {
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val()
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initAccountChart(response.data);
            } else {
                console.error('Error loading account chart data:', response.error);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error loading account chart data:', error);
        }
    });

    // Load material summary data for chart
    $.ajax({
        url: '/groups/warehouse/audit_transactions/material-summary',
        data: {
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val()
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initMaterialChart(response.data);
            } else {
                console.error('Error loading material chart data:', response.error);
            }
        },
        error: function (xhr, status, error) {
            console.error('Error loading material chart data:', error);
        }
    });
}

/**
 * Initialize the account distribution chart
 * @param {Array} data - The account summary data
 */
function initAccountChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get the chart canvas
    const canvas = document.getElementById('accountChart');
    if (!canvas) {
        console.error('Cannot find accountChart canvas element');
        return;
    }

    // Destroy existing chart if it exists
    let existingChart;
    try {
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.warn('No existing chart found or error checking:', e);
    }

    // Prepare data for the chart - use only top 10 accounts for readability
    const topAccounts = data.slice(0, 10);

    // Create chart colors
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(255, 99, 71, 0.7)',
        'rgba(46, 204, 113, 0.7)',
        'rgba(52, 152, 219, 0.7)'
    ];

    const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));

    // Create the chart
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: topAccounts.map(item => item.ACCTNUM),
            datasets: [{
                data: topAccounts.map(item => item.TotalCostDiff),
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 GL Accounts by Cost Change'
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = formatCurrency(context.raw);
                            const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize the material chart
 * @param {Array} data - The material summary data
 */
function initMaterialChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get the chart canvas
    const canvas = document.getElementById('materialChart');
    if (!canvas) {
        console.error('Cannot find materialChart canvas element');
        return;
    }

    // Destroy existing chart if it exists
    let existingChart;
    try {
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.warn('No existing chart found or error checking:', e);
    }

    // Prepare data for the chart - use only top 10 materials for readability
    const topMaterials = data.slice(0, 10);

    // Create the chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: topMaterials.map(item => truncateString(item.DESCRIPTION || item.MATERIALUID, 20)),
            datasets: [{
                label: 'Cost Change',
                data: topMaterials.map(item => item.TotalCostDiff),
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
                    text: 'Top 10 Materials by Cost Change'
                },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            // Show the full description on hover
                            const idx = tooltipItems[0].dataIndex;
                            return topMaterials[idx].DESCRIPTION;
                        },
                        label: function (context) {
                            return `Material ID: ${topMaterials[context.dataIndex].MATERIALUID}`;
                        },
                        afterLabel: function (context) {
                            return `Cost Change: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Cost Change ($)'
                    },
                    ticks: {
                        callback: function (value) {
                            return formatCurrency(value, false);
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Material Description'
                    }
                }
            }
        }
    });
}


/**
 * Update the summary statistics based on the data
 * @param {Array} data - The transaction data
 */
function updateStats(data) {
    if (!data || !data.length) {
        $('#totalTransactions').text('0');
        $('#totalCostChange').text('$0.00');
        $('#uniqueMaterials').text('0');
        $('#dateRangeInfo').text('No data available');
        return;
    }

    // Total transactions
    const totalTransactions = data.length;
    $('#totalTransactions').text(totalTransactions);

    // Total cost change (absolute value)
    const totalCostChange = data.reduce((sum, item) => sum + Math.abs(parseFloat(item.COSTDIFF) || 0), 0);
    $('#totalCostChange').text(formatCurrency(totalCostChange));

    // Unique materials
    const uniqueMaterials = new Set(data.map(item => item.MATERIALUID)).size;
    $('#uniqueMaterials').text(uniqueMaterials);

    // Date range info
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    $('#dateRangeInfo').text(`From ${formatDate(startDate)} to ${formatDate(endDate)}`);
}

/**
 * Export the report data to CSV
 */
function exportReportData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const accountNumber = $('#accountNumber').val();
    const materialId = $('#materialId').val();

    // Build export URL with query parameters
    let url = '/groups/warehouse/audit_transactions/export';
    const params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (accountNumber) params.push(`account_number=${encodeURIComponent(accountNumber)}`);
    if (materialId) params.push(`material_id=${encodeURIComponent(materialId)}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open the export URL in a new tab
    window.open(url, '_blank');
}

/**
 * Format a date for display
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';

        return date.toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
}

/**
 * Format a date and time for display
 * @param {string} dateTimeString - The date/time string to format
 * @returns {string} - Formatted date/time string
 */
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '';

    try {
        const date = new Date(dateTimeString);
        if (isNaN(date.getTime())) return '';

        return date.toLocaleString();
    } catch (error) {
        console.error('Error formatting date/time:', error);
        return '';
    }
}

/**
 * Format a number as currency
 * @param {number|string} value - The value to format
 * @param {boolean} includeSymbol - Whether to include the $ symbol
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value, includeSymbol = true) {
    if (value === null || value === undefined) return includeSymbol ? '$0.00' : '0.00';

    try {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return includeSymbol ? '$0.00' : '0.00';

        const formatter = new Intl.NumberFormat('en-US', {
            style: includeSymbol ? 'currency' : 'decimal',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        return formatter.format(numValue);
    } catch (error) {
        console.error('Error formatting currency:', error);
        return includeSymbol ? '$0.00' : '0.00';
    }
}

/**
 * Truncate a string to a maximum length and add ellipsis if needed
 * @param {string} str - The string to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} - Truncated string
 */
function truncateString(str, maxLength) {
    if (!str) return '';

    if (str.length <= maxLength) {
        return str;
    }

    return str.substring(0, maxLength) + '...';
}

/**
 * Show an error message to the user
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