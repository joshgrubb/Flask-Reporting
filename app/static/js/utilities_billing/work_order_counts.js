/**
 * Work Order Counts Report JavaScript
 * 
 * This file handles the interactive functionality for the Work Order Counts report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#startDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate", {
            dateFormat: "Y-m-d"
        });
    }

    if ($("#endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#endDate", {
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
        // Reset to default dates (last 30 days)
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 30);
        const formattedStartDate = startDate.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(endDate);

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
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalWorkOrders, #topRequestor, #dailyAverage').text('-');
    $('#dateRangeInfo, #topRequestorCount').text('Loading...');

    // Load main data - work orders by user
    $.ajax({
        url: '/groups/utilities_billing/work_order_counts/data',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                updateStats(response.data);
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

    // Load daily counts data
    $.ajax({
        url: '/groups/utilities_billing/work_order_counts/daily-counts',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDailyChart(response.data);
            } else {
                showError('Error loading daily counts data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading daily counts data: ' + error);
        }
    });

    // Load type counts data
    $.ajax({
        url: '/groups/utilities_billing/work_order_counts/type-counts',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initTypeChart(response.data);
            } else {
                showError('Error loading type counts data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading type counts data: ' + error);
        }
    });
}

/**
 * Initialize DataTable with work order count data
 * @param {Array} data - The work order data to display
 */
function initDataTable(data) {
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

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'UserName' },
            { data: 'CountUser' }
        ],
        pageLength: 10,
        order: [[1, 'desc']], // Sort by work order count, highest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#workOrdersTable').DataTable(dataTableOptions);

    // SafeDOM usage for window resize listener
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize Daily Work Orders Chart
 * @param {Array} data - The daily counts data to display
 */
function initDailyChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('dailyWorkOrdersChart');
    if (!canvas) {
        console.error('Cannot find dailyWorkOrdersChart canvas element');
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

    // Format dates for display
    const formattedData = data.map(item => ({
        date: formatDate(item.CreateDate),
        count: item.DailyCount,
        rawDate: new Date(item.CreateDate)
    })).sort((a, b) => a.rawDate - b.rawDate);

    // Calculate average daily count
    if (formattedData.length > 0) {
        const totalCount = formattedData.reduce((sum, item) => sum + item.count, 0);
        const avgCount = (totalCount / formattedData.length).toFixed(1);
        $('#dailyAverage').text(avgCount);
    }

    // Create chart
    try {
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: formattedData.map(item => item.date),
                datasets: [{
                    label: 'Work Order Count',
                    data: formattedData.map(item => item.count),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.3 // Smooth curve
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Work Orders'
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                return tooltipItems[0].label;
                            },
                            label: function (context) {
                                return `Work Orders: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
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
        console.error('Error creating daily chart:', error);
        showError('Failed to create daily chart: ' + error.message);
    }
}

/**
 * Initialize Type Chart
 * @param {Array} data - The type count data to display
 */
function initTypeChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('typeChart');
    if (!canvas) {
        console.error('Cannot find typeChart canvas element');
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
    const labels = data.map(item => item.TypeName || 'Unknown');
    const values = data.map(item => item.TypeCount);

    // Create color palette
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
    ];

    const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));

    // Create chart
    try {
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors.slice(0, values.length),
                    borderColor: borderColors.slice(0, values.length),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
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
        console.error('Error creating type chart:', error);
        showError('Failed to create type chart: ' + error.message);
    }
}

/**
 * Update statistics based on data
 * @param {Array} data - The report data
 */
function updateStats(data) {
    if (!data || !data.length) {
        $('#totalWorkOrders').text('0');
        $('#topRequestor').text('None');
        $('#topRequestorCount').text('No work orders in period');
        $('#dateRangeInfo').text('No data available');
        return;
    }

    // Calculate total work orders
    const totalWorkOrders = data.reduce((sum, row) => sum + row.CountUser, 0);
    $('#totalWorkOrders').text(totalWorkOrders);

    // Find top requestor
    const topRequestor = data[0]; // Data is already sorted by count (highest first)
    $('#topRequestor').text(topRequestor.UserName);
    $('#topRequestorCount').text(`${topRequestor.CountUser} work orders`);

    // Date range info
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    $('#dateRangeInfo').text(`From ${formatDate(startDate)} to ${formatDate(endDate)}`);
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
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/utilities_billing/work_order_counts/export';
    url += `?start_date=${startDate}&end_date=${endDate}`;

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