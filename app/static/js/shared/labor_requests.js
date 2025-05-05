/**
 * Labor Requests Report JavaScript
 * 
 * This file handles the interactive functionality for the Labor Requests report,
 * including loading data, initializing tables, creating charts, and handling user interactions.
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
    loadLaborData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadLaborData();
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

        // Reset category filter
        $('#categorySelect').val('');

        // Reload data with reset filters
        loadLaborData();
    });

    $('#exportData').click(function () {
        exportLaborData();
    });
});

/**
 * Load labor requests data
 */
function loadLaborData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const category = $('#categorySelect').val();

    // Show loading indicator
    $('#dataTableContainer').addClass('loading');

    // Update filter info text
    updateCategoryInfo(category);

    // Load data from API
    $.ajax({
        url: window.location.pathname + 'data',  // Append 'data' to current path
        data: {
            start_date: startDate,
            end_date: endDate,
            category: category
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Initialize table
                initLaborTable(response.data);

                // Update summary stats
                updateSummaryStats(response.data);

                // Create charts
                createCategoryChart(response.data);
                createTimeSeriesChart(response.data);

                // Update date range info
                updateDateRangeInfo(response.filters.start_date, response.filters.end_date);
            } else {
                showError('Error loading labor data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading labor data: ' + error);
        },
        complete: function () {
            $('#dataTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the labor requests data table
 * @param {Array} data - The labor requests data
 */
function initLaborTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#laborRequestsTable')) {
        $('#laborRequestsTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#laborRequestsTable').DataTable({
        data: data,
        columns: [
            { data: 'REQUESTID' },
            { data: 'DESCRIPTION' },
            { data: 'REQCATEGORY' },
            { data: 'LABORNAME' },
            {
                data: 'HOURS',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                data: 'COST',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'TRANSDATE',
                render: function (data) {
                    return formatDateSafe(data);
                }
            }
        ],
        pageLength: 25,
        order: [[6, 'desc']], // Sort by transaction date, newest first
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
}

/**
 * Update summary statistics based on data
 * @param {Array} data - The labor requests data
 */
function updateSummaryStats(data) {
    if (!data || data.length === 0) {
        $('#totalRequests').text('0');
        $('#totalHours').text('0');
        $('#totalCost').text('$0.00');
        $('#averageRate').text('$0.00');
        return;
    }

    // Count unique request IDs
    const uniqueRequests = new Set();
    data.forEach(row => uniqueRequests.add(row.REQUESTID));

    // Calculate total hours
    const totalHours = data.reduce((sum, row) => sum + parseFloat(row.HOURS || 0), 0);

    // Calculate total cost
    const totalCost = data.reduce((sum, row) => sum + parseFloat(row.COST || 0), 0);

    // Calculate average rate
    const avgRate = totalHours > 0 ? totalCost / totalHours : 0;

    // Update UI
    $('#totalRequests').text(uniqueRequests.size);
    $('#totalHours').text(totalHours.toFixed(2));
    $('#totalCost').text(formatCurrency(totalCost));
    $('#averageRate').text(formatCurrency(avgRate));
}

/**
 * Create a chart showing labor hours by category
 * @param {Array} data - The labor requests data
 */
function createCategoryChart(data) {
    if (!data || data.length === 0 || typeof Chart === 'undefined') return;

    // Process data for the chart
    const categoryMap = new Map();

    // Group hours by category
    data.forEach(row => {
        const category = row.REQCATEGORY || 'Uncategorized';
        const hours = parseFloat(row.HOURS || 0);

        if (categoryMap.has(category)) {
            categoryMap.set(category, categoryMap.get(category) + hours);
        } else {
            categoryMap.set(category, hours);
        }
    });

    // Convert map to arrays for the chart
    const categories = Array.from(categoryMap.keys());
    const hours = Array.from(categoryMap.values());

    // Get the canvas element
    const ctx = document.getElementById('categoryChart');

    // Destroy existing chart if it exists
    if (window.categoryChart instanceof Chart) {
        window.categoryChart.destroy();
    }

    // Create a new chart
    window.categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: hours,
                backgroundColor: generateColors(categories.length),
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
                        boxWidth: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.raw;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return context.label + ": " + value.toFixed(1) + " hours (" + percentage + "%)";
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a time series chart showing labor costs over time
 * @param {Array} data - The labor requests data
 */
function createTimeSeriesChart(data) {
    if (!data || data.length === 0 || typeof Chart === 'undefined') return;

    // Process data for the chart
    const dateMap = new Map();

    // Sort data by date
    data.sort((a, b) => {
        return new Date(a.TRANSDATE) - new Date(b.TRANSDATE);
    });

    // Group costs by date (daily)
    data.forEach(row => {
        const dateStr = row.TRANSDATE ? row.TRANSDATE.split('T')[0] : 'Unknown';
        const cost = parseFloat(row.COST || 0);

        if (dateMap.has(dateStr)) {
            dateMap.set(dateStr, dateMap.get(dateStr) + cost);
        } else {
            dateMap.set(dateStr, cost);
        }
    });

    // Convert map to arrays for the chart
    const dates = Array.from(dateMap.keys());
    const costs = Array.from(dateMap.values());

    // Get the canvas element
    const ctx = document.getElementById('timeSeriesChart');

    // Destroy existing chart if it exists
    if (window.timeSeriesChart instanceof Chart) {
        window.timeSeriesChart.destroy();
    }

    // Create a new chart
    window.timeSeriesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Labor Cost',
                data: costs,
                borderColor: '#4361ee',
                backgroundColor: 'rgba(67, 97, 238, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cost ($)'
                    },
                    ticks: {
                        callback: function (value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return 'Cost: ' + formatCurrency(context.raw);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update category info in the UI
 * @param {string} category - The selected category
 */
function updateCategoryInfo(category) {
    if (category) {
        $('#categoryInfo').text('Category: ' + category);
    } else {
        $('#categoryInfo').text('All categories');
    }
}

/**
 * Update date range info in the UI
 * @param {string} startDate - The start date
 * @param {string} endDate - The end date
 */
function updateDateRangeInfo(startDate, endDate) {
    $('#dateRangeInfo').text('From ' + formatDateSafe(startDate) + ' to ' + formatDateSafe(endDate));
}

/**
 * Export labor requests data to CSV
 */
function exportLaborData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const category = $('#categorySelect').val();

    // Build export URL
    let url = window.location.pathname + 'export';
    let params = [];

    if (startDate) params.push('start_date=' + startDate);
    if (endDate) params.push('end_date=' + endDate);
    if (category) params.push('category=' + category);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Generate an array of colors for the charts
 * @param {number} count - Number of colors needed
 * @returns {Array} Array of color strings
 */
function generateColors(count) {
    // Base colors
    const baseColors = [
        '#4361ee', // Primary
        '#4cc9f0', // Secondary
        '#f72585', // Accent
        '#10b981', // Success
        '#f59e0b', // Warning
        '#ef4444'  // Danger
    ];

    // If we need more colors than in the base set
    if (count <= baseColors.length) {
        return baseColors.slice(0, count);
    } else {
        // Generate additional colors by adjusting hue
        const colors = [...baseColors];
        const hueStep = 360 / (count - baseColors.length);

        for (let i = 0; i < count - baseColors.length; i++) {
            // Use HSL to generate colors with consistent lightness/saturation
            const hue = (i * hueStep) % 360;
            colors.push('hsl(' + hue + ', 70%, 60%)');
        }

        return colors;
    }
}

/**
 * Format a date string safely without timezone shifting
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDateSafe(dateString) {
    if (!dateString) return '';

    try {
        // Extract date components directly from YYYY-MM-DD format
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);

            // Create date without timezone shifting
            const date = new Date(year, month, day);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                return dateString; // Return original if parsing failed
            }

            // Format using locale-specific date format
            return date.toLocaleDateString();
        }

        // Fallback to original format function if not in expected format
        return formatDate(dateString);
    } catch (error) {
        console.error('Error safely formatting date:', error);
        return dateString;
    }
}

/**
 * Format a number as currency
 * @param {number|string} value - The number to format as currency
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value) {
    if (value === null || value === undefined || value === '') return '$0.00';

    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '$0.00';

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numValue);
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
    alertDiv.innerHTML =
        '<i class="fas fa-exclamation-triangle me-2"></i>' +
        '<strong>Error:</strong> ' + message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';

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