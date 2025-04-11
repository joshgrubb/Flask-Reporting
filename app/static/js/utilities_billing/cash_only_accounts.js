/**
 * Cash Only Accounts Report JavaScript
 * 
 * This file handles the interactive functionality for the Cash Only Accounts report,
 * including loading data, initializing charts, and handling user interactions.
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

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Clear date inputs
        $('#startDate').val('');
        $('#endDate').val('');
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
    $('#totalAccounts, #noEndDateCount, #dateRange').text('-');
    $('#daysSinceFirst').text('Loading...');

    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/cash_only_accounts/data',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                initAccountsChart(response.data);
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
        url: '/groups/utilities_billing/cash_only_accounts/summary',
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
                data: 'MessageStartDate',
                render: function (data) {
                    return formatDate(data);
                }
            },
            {
                data: 'MessageEndDate',
                render: function (data) {
                    return data ? formatDate(data) : '<span class="text-warning">No End Date</span>';
                }
            },
            { data: 'Message' },
            {
                data: null,
                render: function (data, type, row) {
                    const endDate = row.MessageEndDate;
                    if (!endDate) {
                        return '<span class="badge bg-warning">Indefinite</span>';
                    }

                    const today = new Date();
                    const end = new Date(endDate);

                    const daysLeft = Math.ceil((end - today) / (1000 * 60 * 60 * 24));

                    if (daysLeft > 30) {
                        return '<span class="badge bg-success">Active</span>';
                    } else if (daysLeft > 0) {
                        return '<span class="badge bg-warning">Expires Soon</span>';
                    } else {
                        return '<span class="badge bg-danger">Expired</span>';
                    }
                }
            }
        ],
        pageLength: 10,
        order: [[1, 'desc']], // Sort by Start Date, newest first
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
 * Initialize chart showing accounts over time
 * @param {Array} data - The account data
 */
function initAccountsChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Process data for chart
    const accountsTimeline = processAccountsTimeline(data);

    // Get canvas element
    const canvas = document.getElementById('accountsChart');
    if (!canvas) {
        console.error('Cannot find accountsChart canvas element');
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
            type: 'line',
            data: {
                labels: accountsTimeline.labels,
                datasets: [{
                    label: 'Cash Only Accounts',
                    data: accountsTimeline.counts,
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: textColor
                        }
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
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        },
                        title: {
                            display: true,
                            text: 'Date',
                            color: textColor
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            precision: 0
                        },
                        title: {
                            display: true,
                            text: 'Number of Accounts',
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
 * Process account data into a timeline for the chart
 * @param {Array} data - The account data
 * @returns {Object} - Object with labels and counts arrays
 */
function processAccountsTimeline(data) {
    // Sort data by start date
    const sortedData = [...data].sort((a, b) => {
        return new Date(a.MessageStartDate) - new Date(b.MessageStartDate);
    });

    // Initialize result
    const result = {
        labels: [],
        counts: []
    };

    // If no data, return empty result
    if (!sortedData.length) {
        return result;
    }

    // Group data by month
    const monthlyData = {};
    const today = new Date();

    // Process start and end dates
    sortedData.forEach(account => {
        const startDate = new Date(account.MessageStartDate);
        const endDate = account.MessageEndDate ? new Date(account.MessageEndDate) : null;

        // Create a date range from start to end (or today if no end date)
        let currentDate = new Date(startDate);
        const lastDate = endDate && endDate < today ? endDate : today;

        while (currentDate <= lastDate) {
            const monthKey = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
            monthlyData[monthKey] = (monthlyData[monthKey] || 0) + 1;

            // Move to next month
            currentDate.setMonth(currentDate.getMonth() + 1);
        }
    });

    // Convert to array and sort chronologically by using the monthKey format YYYY-MM
    const sortedMonths = Object.keys(monthlyData).sort();

    // Format labels and get counts
    result.labels = sortedMonths.map(monthKey => {
        const [year, month] = monthKey.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1, 1);
        return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short' });
    });

    result.counts = sortedMonths.map(monthKey => monthlyData[monthKey]);

    return result;
}

/**
 * Update summary statistics
 * @param {Object} data - The summary data
 */
function updateSummaryStats(data) {
    if (!data) return;

    // Update total accounts
    $('#totalAccounts').text(data.TotalAccounts || 0);

    // Update accounts with no end date
    $('#noEndDateCount').text(data.NoEndDateCount || 0);

    // Update date range
    const oldestDate = data.OldestMessageDate ? formatDate(data.OldestMessageDate) : 'N/A';
    const newestDate = data.NewestMessageDate ? formatDate(data.NewestMessageDate) : 'N/A';
    $('#dateRange').text(`${oldestDate} to ${newestDate}`);

    // Update days since first account
    const daysSince = data.DaysSinceOldest || 0;
    $('#daysSinceFirst').text(`${daysSince} days since first account`);
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/utilities_billing/cash_only_accounts/export';

    // Add query parameters if filters are set
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);

    if (params.length > 0) {
        url += `?${params.join('&')}`;
    }

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