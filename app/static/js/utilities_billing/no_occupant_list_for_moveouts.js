/**
 * No Occupant List for Moveouts Report JavaScript
 * 
 * This file handles the interactive functionality for the No Occupant List for Moveouts report,
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
        // Reset to default dates (last 90 days)
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 90);
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
    $('#totalVacant').text('-');
    $('#dateRangeInfo').text('Loading...');

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/no_occupant_list_for_moveouts/data',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                updateTotalStats(response.data);
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
        url: '/groups/utilities_billing/no_occupant_list_for_moveouts/summary',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initAgeDistributionChart(response.data);
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
 * Initialize DataTable with moveouts data
 * @param {Array} data - The moveouts data to display
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#moveoutsTable')) {
        $('#moveoutsTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'FullAccountNumber' },
            { data: 'FullAddress' },
            {
                data: 'DaysFromMoveOut',
                render: function (data) {
                    // Color-code based on days
                    let className = '';
                    if (data > 90) {
                        className = 'days-critical';
                    } else if (data > 60) {
                        className = 'days-warning';
                    } else {
                        className = 'days-normal';
                    }

                    return '<span class="' + className + '">' + data + '</span>';
                }
            },

        ],
        pageLength: 10,
        order: [[2, 'desc']], // Sort by Days Since Moveout, highest first
        dom: 'Bfrtip',
        buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#moveoutsTable').DataTable(dataTableOptions);

    // SafeDOM usage for window resize listener
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize Age Distribution Chart
 * @param {Array} data - The age distribution data to display
 */
function initAgeDistributionChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('ageDistributionChart');
    if (!canvas) {
        console.error('Cannot find ageDistributionChart canvas element');
        return;
    }

    // Safely destroy existing chart if it exists
    // Check both the window object and the canvas object
    if (window.ageDistributionChart) {
        if (typeof window.ageDistributionChart.destroy === 'function') {
            window.ageDistributionChart.destroy();
        } else {
            // If the chart object exists but doesn't have a destroy method,
            // it might be corrupted, so we'll clear it.
            window.ageDistributionChart = null;
        }
    }

    // Check if there's a Chart instance attached to the canvas
    const chartInstance = Chart.getChart(canvas);
    if (chartInstance) {
        chartInstance.destroy();
    }

    // Prepare data for the chart
    const labels = data.map(item => item.AgeGroup);
    const values = data.map(item => item.AddressCount);

    // Create chart colors
    const colors = [
        'rgba(76, 175, 80, 0.7)',   // Green for 0-30 days
        'rgba(255, 152, 0, 0.7)',   // Orange for 31-60 days
        'rgba(255, 87, 34, 0.7)',   // Deep Orange for 61-90 days
        'rgba(211, 47, 47, 0.7)'    // Red for over 90 days
    ];

    const borderColors = [
        'rgba(76, 175, 80, 1)',     // Green
        'rgba(255, 152, 0, 1)',     // Orange
        'rgba(255, 87, 34, 1)',     // Deep Orange
        'rgba(211, 47, 47, 1)'      // Red
    ];

    // Create new chart
    try {
        window.ageDistributionChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Vacant Addresses',
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
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.raw} addresses`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
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
 * Update total statistics based on data
 * @param {Array} data - The report data
 */
function updateTotalStats(data) {
    if (!data || !data.length) {
        $('#totalVacant').text('0');
        $('#dateRangeInfo').text('No data available');
        return;
    }

    // Total vacant addresses
    const totalVacant = data.length;
    $('#totalVacant').text(totalVacant);

    // Date range info
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    $('#dateRangeInfo').text(`Moveouts from ${formatDateSafe(startDate)} to ${formatDateSafe(endDate)}`);
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
 * Export report data to CSV
 */
function exportReportData() {
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/utilities_billing/no_occupant_list_for_moveouts/export';
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