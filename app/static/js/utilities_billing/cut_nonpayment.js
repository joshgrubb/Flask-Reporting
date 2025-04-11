/**
 * Cut for Nonpayment Report JavaScript
 * 
 * This file handles the interactive functionality for the Cut for Nonpayment report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#cutDateInput").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#cutDateInput", {
            dateFormat: "Y-m-d",
            maxDate: "today"
        });
    }

    // Initialize multiselect for cycles
    if ($.fn.multiselect) {
        $('#cycleSelect').multiselect({
            includeSelectAllOption: true,
            nonSelectedText: 'All Cycles',
            enableFiltering: true
        });
    }

    // Initial data load
    loadAllData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Reset date to 30 days ago
        const defaultDate = new Date();
        defaultDate.setDate(defaultDate.getDate() - 30);
        const formattedDate = defaultDate.toISOString().slice(0, 10);
        $('#cutDateInput').val(formattedDate);

        // Reset cycles to nothing selected (which means all)
        if ($.fn.multiselect) {
            $('#cycleSelect').multiselect('deselectAll', false);
            $('#cycleSelect').multiselect('updateButtonText');
        } else {
            $('#cycleSelect').val([]);
        }

        // Reload data
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
    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#chartContainer').addClass('loading');
    $('#totalAccounts, #totalCuts, #avgCutsPerAccount').text('-');

    // Get filter values
    const cutDate = $('#cutDateInput').val();
    const selectedCycles = $('#cycleSelect').val() || [];
    const cycleParam = selectedCycles.join(',');

    // Prepare filter params
    const filterParams = {};
    if (cutDate) filterParams.cut_date = cutDate;
    if (cycleParam) filterParams.cycles = cycleParam;

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/cut_nonpayment/data',
        data: filterParams,
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                updateBasicStats(response.data);
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

    // Load summary data for charts
    $.ajax({
        url: '/groups/utilities_billing/cut_nonpayment/summary',
        data: filterParams,
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initSummaryCharts(response.data);
            } else {
                showError('Error loading summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading summary data: ' + error);
        },
        complete: function () {
            $('#chartContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize DataTable with accounts data
 * @param {Array} data - The accounts data to display
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
            { data: 'LastName' },
            { data: 'FirstName' },
            { data: 'FullAddress' },
            { data: 'Cycle' },
            { data: 'AccountType' },
            {
                data: 'CUTS',
                render: function (data) {
                    // Apply styling based on number of cuts
                    let badgeClass = 'bg-warning';
                    if (data >= 3) {
                        badgeClass = 'bg-danger';
                    } else if (data == 1) {
                        badgeClass = 'bg-info';
                    }
                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }
            }
        ],
        pageLength: 25,
        order: [[6, 'desc']], // Sort by number of cuts, highest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        rowCallback: function (row, data) {
            // Add classes based on cut count
            if (data.CUTS >= 3) {
                $(row).addClass('table-danger');
            } else if (data.CUTS == 2) {
                $(row).addClass('table-warning');
            }
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
 * Initialize summary charts
 * @param {Array} summaryData - The summary data for charts
 */
function initSummaryCharts(summaryData) {
    if (!summaryData || !summaryData.length) {
        // Show no data message
        $('#chartContainer').html('<div class="alert alert-info">No summary data available for the selected filters.</div>');
        return;
    }

    // Initialize the chart container if empty
    if ($('#chartContainer').children().length === 0) {
        $('#chartContainer').html(`
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-box">
                        <h5>Cuts by Cycle</h5>
                        <canvas id="cycleCutsChart"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-box">
                        <h5>Cuts by Account Type</h5>
                        <canvas id="accountTypeCutsChart"></canvas>
                    </div>
                </div>
            </div>
        `);
    }

    // Process data for charts
    const processedData = processSummaryData(summaryData);

    // Initialize cycle chart
    initCycleChart(processedData.byCycle);

    // Initialize account type chart
    initAccountTypeChart(processedData.byAccountType);
}

/**
 * Process summary data for charts
 * @param {Array} summaryData - Raw summary data from API
 * @returns {Object} - Processed data for charts
 */
function processSummaryData(summaryData) {
    // Initialize result structures
    const byCycle = {
        labels: [],
        data: [],
        colors: []
    };

    const byAccountType = {
        labels: [],
        data: [],
        colors: []
    };

    // Process by cycle
    const cycleMap = {};
    const accountTypeMap = {};

    // First pass - collect unique cycles and account types
    summaryData.forEach(item => {
        if (!cycleMap[item.Cycle]) {
            cycleMap[item.Cycle] = 0;
        }

        if (!accountTypeMap[item.AccountType]) {
            accountTypeMap[item.AccountType] = 0;
        }

        // Add to totals
        cycleMap[item.Cycle] += parseInt(item.AccountCount);
        accountTypeMap[item.AccountType] += parseInt(item.AccountCount);
    });

    // Generate colors - base palette
    const palette = [
        'rgba(54, 162, 235, 0.7)',  // blue
        'rgba(255, 99, 132, 0.7)',  // red
        'rgba(255, 206, 86, 0.7)',  // yellow
        'rgba(75, 192, 192, 0.7)',  // green
        'rgba(153, 102, 255, 0.7)', // purple
        'rgba(255, 159, 64, 0.7)',  // orange
        'rgba(201, 203, 207, 0.7)'  // grey
    ];

    // Convert to arrays for charts
    let colorIndex = 0;
    Object.keys(cycleMap).sort().forEach(cycle => {
        byCycle.labels.push(cycle);
        byCycle.data.push(cycleMap[cycle]);
        byCycle.colors.push(palette[colorIndex % palette.length]);
        colorIndex++;
    });

    colorIndex = 0;
    Object.keys(accountTypeMap).sort().forEach(type => {
        byAccountType.labels.push(type);
        byAccountType.data.push(accountTypeMap[type]);
        byAccountType.colors.push(palette[colorIndex % palette.length]);
        colorIndex++;
    });

    return {
        byCycle,
        byAccountType
    };
}

/**
 * Initialize cycle chart
 * @param {Object} data - Processed cycle data
 */
function initCycleChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('cycleCutsChart');
    if (!canvas) {
        console.error('Cannot find cycleCutsChart canvas element');
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
                labels: data.labels,
                datasets: [{
                    label: 'Accounts with Cuts',
                    data: data.data,
                    backgroundColor: data.colors,
                    borderColor: data.colors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                return `Cycle: ${tooltipItems[0].label}`;
                            },
                            label: function (context) {
                                return `Accounts: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    },
                    y: {
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
        console.error('Error creating cycle chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Initialize account type chart
 * @param {Object} data - Processed account type data
 */
function initAccountTypeChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('accountTypeCutsChart');
    if (!canvas) {
        console.error('Cannot find accountTypeCutsChart canvas element');
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

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';

    // Create new chart - pie chart for account types
    try {
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.colors,
                    borderColor: data.colors.map(color => color.replace('0.7', '1')),
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
    } catch (error) {
        console.error('Error creating account type chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Update basic statistics
 * @param {Array} data - The report data
 */
function updateBasicStats(data) {
    if (!data || !data.length) {
        $('#totalAccounts').text('0');
        $('#totalCuts').text('0');
        $('#avgCutsPerAccount').text('0');
        return;
    }

    // Calculate basic statistics
    const totalAccounts = data.length;

    // Sum all cuts
    let totalCuts = 0;
    data.forEach(account => {
        totalCuts += parseInt(account.CUTS || 0);
    });

    // Calculate average
    const avgCuts = totalAccounts > 0 ? (totalCuts / totalAccounts).toFixed(1) : '0.0';

    // Update the stats displays
    $('#totalAccounts').text(totalAccounts);
    $('#totalCuts').text(totalCuts);
    $('#avgCutsPerAccount').text(avgCuts);

    // Update date info
    const cutDate = $('#cutDateInput').val() || 'Last 30 days';
    $('#dateRangeInfo').text(`Since ${cutDate}`);
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Get filter values for export URL
    const cutDate = $('#cutDateInput').val();
    const selectedCycles = $('#cycleSelect').val() || [];
    const cycleParam = selectedCycles.join(',');

    // Build export URL with query parameters
    let url = '/groups/utilities_billing/cut_nonpayment/export';
    const params = [];

    if (cutDate) {
        params.push(`cut_date=${encodeURIComponent(cutDate)}`);
    }

    if (cycleParam) {
        params.push(`cycles=${encodeURIComponent(cycleParam)}`);
    }

    if (params.length > 0) {
        url += '?' + params.join('&');
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