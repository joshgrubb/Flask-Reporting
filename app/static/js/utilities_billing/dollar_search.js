/**
 * Dollar Search Report JavaScript
 * 
 * This file handles the interactive functionality for the Dollar Search report,
 * including form handling, data loading, chart rendering, and results display.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker if available
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initialize event handlers
    $('#searchForm').on('submit', function (e) {
        e.preventDefault();
        performSearch();
    });

    $('#resetButton').click(function () {
        resetForm();
    });

    $('#exportButton').click(function () {
        exportResults();
    });
});

/**
 * Perform search based on form inputs
 */
function performSearch() {
    // Get search parameters
    const amount = $('#amountInput').val().trim();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Validate amount
    if (!amount || isNaN(parseFloat(amount))) {
        showError('Please enter a valid dollar amount');
        return;
    }

    // Build query parameters
    const params = new URLSearchParams();
    params.append('amount', amount);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    // Show loading indicator
    showLoading(true);

    // Hide messages and results
    $('#initialMessage').hide();
    $('#noResultsMessage').hide();
    $('#resultsOverview').hide();
    $('#chartSection').hide();
    $('#resultsTableContainer').hide();

    // Perform AJAX request
    $.ajax({
        url: '/groups/utilities_billing/dollar_search/search',
        data: params.toString(),
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                displayResults(response);
            } else {
                showError('Error loading data: ' + response.error);
                $('#noResultsMessage').show();
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading data: ' + error);
            $('#noResultsMessage').show();
        },
        complete: function () {
            showLoading(false);
        }
    });
}

/**
 * Display search results
 * @param {Object} response - The response from the server
 */
function displayResults(response) {
    const { data, counts, total_count, filters } = response;

    // Show results overview section
    $('#resultsOverview').show();

    // Update summary statistics
    $('#totalMatches').text(total_count);
    $('#searchCriteria').text(`Amount: ${formatCurrency(filters.amount)}`);

    // Update date range display
    const startDate = filters.start_date ? formatDateSafe(filters.start_date) : '30 days ago';
    const endDate = filters.end_date ? formatDateSafe(filters.end_date) : 'today';
    $('#dateRange').text(`${startDate} to ${endDate}`);

    // Display appropriate message if no results
    if (total_count === 0) {
        $('#noResultsMessage').show();
        return;
    }

    // Initialize chart with payment type counts
    initPaymentTypeChart(counts);
    $('#chartSection').show();

    // Initialize data table with results
    initDataTable(data);
    $('#resultsTableContainer').show();
}

/**
 * Initialize DataTable with search results
 * @param {Array} data - The search results data
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#resultsTable')) {
        $('#resultsTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'AccountOrRef' },
            {
                data: 'Amount',
                render: function (data) {
                    // Format amount as currency
                    return formatCurrency(data);
                }
            },
            {
                data: 'TransactionDate',
                render: function (data) {
                    return formatDateTime(data);
                }
            },
            {
                data: 'PaymentType',
                render: function (data) {
                    // Apply styling based on payment type
                    let badgeClass = '';
                    if (data === 'Utility Payment') {
                        badgeClass = 'bg-primary';
                    } else if (data === 'Online Payment') {
                        badgeClass = 'bg-success';
                    } else if (data === 'Cash/Check Payment') {
                        badgeClass = 'bg-info';
                    }
                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }
            }
        ],
        pageLength: 10,
        order: [[2, 'desc']], // Sort by Transaction Date, newest first
        language: {
            search: "Filter:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#resultsTable').DataTable(dataTableOptions);

    // Responsive adjustment on window resize
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize pie chart for payment type breakdown
 * @param {Array} counts - The payment type count data
 */
function initPaymentTypeChart(counts) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('paymentTypeChart');
    if (!canvas) {
        console.error('Cannot find paymentTypeChart canvas element');
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
    const labels = counts.map(item => item.PaymentType);
    const values = counts.map(item => item.TransactionCount);

    // Define colors for payment types
    const colors = {
        'Utility Payment': 'rgba(54, 162, 235, 0.7)',
        'Online Payment': 'rgba(75, 192, 192, 0.7)',
        'Cash/Check Payment': 'rgba(255, 159, 64, 0.7)'
    };

    const borderColors = {
        'Utility Payment': 'rgba(54, 162, 235, 1)',
        'Online Payment': 'rgba(75, 192, 192, 1)',
        'Cash/Check Payment': 'rgba(255, 159, 64, 1)'
    };

    // Create color arrays based on payment types
    const backgroundColors = labels.map(label => colors[label] || 'rgba(201, 203, 207, 0.7)');
    const borderColorArray = labels.map(label => borderColors[label] || 'rgba(201, 203, 207, 1)');

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';

    // Create new chart
    try {
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderColor: borderColorArray,
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
        console.error('Error creating chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Reset the search form
 */
function resetForm() {
    // Clear amount input
    $('#amountInput').val('');

    // Reset dates to default (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    $('#startDate').val(thirtyDaysAgo.toISOString().slice(0, 10));
    $('#endDate').val(today.toISOString().slice(0, 10));

    // Reset display
    $('#resultsOverview').hide();
    $('#chartSection').hide();
    $('#resultsTableContainer').hide();
    $('#noResultsMessage').hide();
    $('#initialMessage').show();

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#resultsTable')) {
        $('#resultsTable').DataTable().destroy();
    }

    // Focus on amount input
    $('#amountInput').focus();
}

/**
 * Export results to CSV
 */
function exportResults() {
    const amount = $('#amountInput').val().trim();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    if (!amount || isNaN(parseFloat(amount))) {
        showError('Please perform a valid search before exporting');
        return;
    }

    // Build export URL with query parameters
    let url = '/groups/utilities_billing/dollar_search/export?amount=' + encodeURIComponent(amount);
    if (startDate) url += '&start_date=' + encodeURIComponent(startDate);
    if (endDate) url += '&end_date=' + encodeURIComponent(endDate);

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Show/hide loading indicator
 * @param {boolean} isLoading - Whether loading is in progress
 */
function showLoading(isLoading) {
    if (isLoading) {
        $('body').addClass('wait');
        $('#resultsTableContainer').addClass('loading');
        $('#searchButton').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Searching...');
    } else {
        $('body').removeClass('wait');
        $('#resultsTableContainer').removeClass('loading');
        $('#searchButton').prop('disabled', false).html('<i class="fas fa-search"></i> Search');
    }
}

/**
 * Format a number as currency
 * @param {number|string} value - The number to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value) {
    if (value == null) return '$0.00';

    try {
        // Parse the value to make sure it's a number
        const numValue = parseFloat(value);

        if (isNaN(numValue)) return '$0.00';

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(numValue);
    } catch (error) {
        console.error('Error formatting currency:', error);
        return '$0.00';
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
 * Format a datetime string safely without timezone shifting
 * @param {string} dateTimeString - The datetime string to format (e.g., "2025-04-01 14:30:00")
 * @param {boolean} includeTime - Whether to include time in the formatted output (default: true)
 * @returns {string} - Formatted datetime string
 */
function formatDateTime(dateTimeString, includeTime = true) {
    if (!dateTimeString) return '';

    try {
        // Extract date and time components directly from string
        // Match format like "2025-04-01 14:30:00" or "2025-04-01T14:30:00"
        const match = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})/);

        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);
            const hours = parseInt(match[4], 10);
            const minutes = parseInt(match[5], 10);
            const seconds = parseInt(match[6], 10);

            // Create date without timezone shifting by specifying all components
            const date = new Date(year, month, day, hours, minutes, seconds);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                console.warn('Invalid date created from:', dateTimeString);
                return dateTimeString; // Return original if parsing failed
            }

            // Format options
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            // Add time options if requested
            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true; // Use 12-hour format (AM/PM)
            }

            // Format using locale-specific datetime format
            return date.toLocaleString(undefined, options);
        }

        // Check for date-only format (YYYY-MM-DD)
        const dateOnlyMatch = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (dateOnlyMatch) {
            const year = parseInt(dateOnlyMatch[1], 10);
            const month = parseInt(dateOnlyMatch[2], 10) - 1;
            const day = parseInt(dateOnlyMatch[3], 10);

            const date = new Date(year, month, day);

            if (isNaN(date.getTime())) {
                return dateTimeString;
            }

            return date.toLocaleDateString();
        }

        // If no pattern matches, try direct parsing as fallback
        // (but this may cause timezone shifts)
        const directDate = new Date(dateTimeString);
        if (!isNaN(directDate.getTime())) {
            console.warn('Using direct date parsing which may cause timezone shifts:', dateTimeString);

            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true;
            }

            return directDate.toLocaleString(undefined, options);
        }

        // Return original string if all parsing attempts fail
        return dateTimeString;
    } catch (error) {
        console.error('Error formatting datetime:', error);
        return dateTimeString;
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