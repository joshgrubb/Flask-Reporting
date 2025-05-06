/**
 * Sewer Clean Length Report JavaScript
 * 
 * This file handles the interactive functionality for the Sewer Clean Length report,
 * including loading data, initializing tables and charts, and handling user interactions.
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
    loadData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadData();
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

        // Reload data with reset filters
        loadData();
    });

    $('#exportData').click(function () {
        exportDetailedData();
    });

    $('#exportSummary').click(function () {
        exportSummaryData();
    });
});

/**
 * Load sewer clean length data
 */
function loadData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicator
    $('#dataTableContainer').addClass('loading');

    // Update filter info text
    updateDateRangeInfo(startDate, endDate);

    // Load data from API
    $.ajax({
        url: '/groups/water_resources/sewer_clean_length/data',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Initialize data table with the detailed data
                initDataTable(response.data);

                // Update summary stats
                updateSummaryStats(response.summary);

                // Initialize charts
                initDailyChart(response.daily_totals);
                initTypeChart(response.description_totals);
            } else {
                showError('Error loading sewer clean length data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading sewer clean length data: ' + error);
        },
        complete: function () {
            $('#dataTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the data table
 * @param {Array} data - The sewer clean data
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#sewerCleanTable')) {
        $('#sewerCleanTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#sewerCleanTable').DataTable({
        data: data,
        columns: [
            { data: 'workorderid' },
            { data: 'description' },
            { data: 'entityuid' },
            { data: 'objectid' },
            {
                data: 'actualfinishdate',
                render: function (data) {
                    return formatDate(data);
                }
            },
            {
                data: 'length_ft',
                render: function (data) {
                    return data ? parseFloat(data).toFixed(2) : '0.00';
                }
            }
        ],
        pageLength: 25,
        order: [[4, 'desc']], // Sort by finish date, newest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    });

    // Handle window resize
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });

    // Remove loading indicator
    $('#dataTableContainer').removeClass('loading');
}

/**
 * Initialize the daily cleaning chart
 * @param {Array} data - The daily totals data
 */
function initDailyChart(data) {
    // Check if Chart.js is available
    if (typeof Chart !== 'function') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Prepare chart data
    const labels = [];
    const lengthData = [];

    // Sort data by date (ascending)
    const sortedData = [...data].sort((a, b) => {
        return new Date(a.clean_date) - new Date(b.clean_date);
    });

    // Extract data for chart
    sortedData.forEach(item => {
        labels.push(formatDate(item.clean_date));
        lengthData.push(parseFloat(item.total_length_ft).toFixed(2));
    });

    // Get the canvas element
    const canvas = document.getElementById('dailyChart');

    // Destroy existing chart if it exists
    if (canvas.chart) {
        canvas.chart.destroy();
    }

    // Create the chart
    const ctx = canvas.getContext('2d');
    canvas.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Length Cleaned (ft)',
                data: lengthData,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Length (ft)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Length: ${context.parsed.y} ft`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize the work type chart
 * @param {Array} data - The work type totals data
 */
function initTypeChart(data) {
    // Check if Chart.js is available
    if (typeof Chart !== 'function') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Prepare chart data
    const labels = [];
    const lengthData = [];
    const countData = [];

    // Extract data for chart
    data.forEach(item => {
        labels.push(item.work_type);
        lengthData.push(parseFloat(item.total_length_ft).toFixed(2));
        countData.push(item.work_order_count);
    });

    // Get the canvas element
    const canvas = document.getElementById('typeChart');

    // Destroy existing chart if it exists
    if (canvas.chart) {
        canvas.chart.destroy();
    }

    // Create the chart
    const ctx = canvas.getContext('2d');
    canvas.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Length Cleaned (ft)',
                    data: lengthData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Work Order Count',
                    data: countData,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1',
                    type: 'line'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Length (ft)'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    title: {
                        display: true,
                        text: 'Work Order Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Work Type'
                    }
                }
            }
        }
    });
}

/**
 * Update summary statistics display
 * @param {Object} summary - The summary data
 */
function updateSummaryStats(summary) {
    // Format the total length
    const totalLengthFt = parseFloat(summary.total_length_ft).toFixed(2);

    // Update the total length display
    $('#totalLength').text(`${totalLengthFt} ft`);

    // Update work order count
    $('#totalWorkOrders').text(summary.total_work_orders);

    // Calculate and update average length
    let avgLength = 0;
    if (summary.total_work_orders > 0) {
        avgLength = (summary.total_length_ft / summary.total_work_orders).toFixed(2);
    }
    $('#avgLength').text(`${avgLength} ft`);
}

/**
 * Update date range information display
 * @param {string} startDate - The start date
 * @param {string} endDate - The end date
 */
function updateDateRangeInfo(startDate, endDate) {
    const formattedStartDate = formatDate(startDate);
    const formattedEndDate = formatDate(endDate);
    $('#dateRangeInfo').text(`From ${formattedStartDate} to ${formattedEndDate}`);
}

/**
 * Export detailed sewer clean data to CSV
 */
function exportDetailedData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/water_resources/sewer_clean_length/export';
    let params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Export summary sewer clean data to CSV
 */
function exportSummaryData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/water_resources/sewer_clean_length/summary-export';
    let params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Format a date string
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);

        // Check if date is valid
        if (isNaN(date.getTime())) {
            return dateString;
        }

        // Format as MM/DD/YYYY
        return date.toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
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