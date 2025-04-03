/**
 * Amount Billed Search Report JavaScript
 * 
 * This file handles the interactive functionality for the Amount Billed Search report,
 * including loading data, initializing the results table, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
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

    // Focus on the search input
    $('#amountInput').focus();
});

/**
 * Perform search based on form inputs
 */
function performSearch() {
    // Get search parameter
    const amount = $('#amountInput').val().trim();

    if (!amount) {
        showError('Please enter a bill amount to search for');
        return;
    }

    // Show loading indicator
    showLoading(true);

    // Hide previous results messages
    $('#noSearchPerformed').addClass('d-none');
    $('#noResultsFound').addClass('d-none');
    $('#resultsSummary').addClass('d-none');

    // Perform AJAX request
    $.ajax({
        url: '/groups/utilities_billing/amount_billed_search/search',
        data: { amount: amount },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                displayResults(response.data, response.count, amount);
            } else {
                showError('Error loading data: ' + response.error);
                $('#noResultsFound').removeClass('d-none');
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading data: ' + error);
            $('#noResultsFound').removeClass('d-none');
        },
        complete: function () {
            showLoading(false);
        }
    });
}

/**
 * Display search results in the table
 * @param {Array} data - The search results data
 * @param {number} count - The total count of results
 * @param {string} searchTerm - The search term used
 */
function displayResults(data, count, searchTerm) {
    // Update results count
    $('#resultsCount').text(count);
    $('#resultsSummary').removeClass('d-none');

    // Show/hide appropriate messages
    if (count === 0) {
        $('#noResultsFound').removeClass('d-none');
        $('#resultsTableContainer').addClass('d-none');
        return;
    } else {
        $('#noResultsFound').addClass('d-none');
        $('#resultsTableContainer').removeClass('d-none');
    }

    // Initialize DataTable
    initDataTable(data, searchTerm);
}

/**
 * Initialize DataTable with the search results
 * @param {Array} data - The search results data
 * @param {string} searchTerm - The search term used
 */
function initDataTable(data, searchTerm) {
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
            {
                data: 'BillAmount',
                render: function (data) {
                    // Format bill amount as currency
                    return `<span class="money">${formatCurrency(data)}</span>`;
                }
            },
            { data: 'FullAccountNumber' },
            {
                data: 'AuditDate',
                render: function (data) {
                    return formatDate(data);
                }
            }
        ],
        pageLength: 10,
        order: [[2, 'desc']], // Sort by AuditDate, newest first
        dom: 'Bfrtip',
        language: {
            search: "Filter:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        initComplete: function () {
            // Highlight the search term in the bill amount column
            // Only if search term is not a wildcard
            if (searchTerm && !searchTerm.includes('%')) {
                highlightSearchTerm(searchTerm);
            }
        }
    };

    // Initialize DataTable
    const table = $('#resultsTable').DataTable(dataTableOptions);

    // Window resize listener for responsive behavior
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Highlight search term in the results
 * @param {string} term - The search term to highlight
 */
function highlightSearchTerm(term) {
    // Clean the term of any special regex characters
    const cleanTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    // Create a case-insensitive regex for the search term
    const regex = new RegExp(`(${cleanTerm})`, 'gi');

    // Apply highlighting to visible rows
    $('.money').each(function () {
        const current = $(this).html();
        const highlighted = current.replace(regex, '<span class="highlight">$1</span>');
        $(this).html(highlighted);
    });
}

/**
 * Reset the search form and clear results
 */
function resetForm() {
    // Clear form fields
    $('#amountInput').val('');

    // Destroy DataTable if it exists
    if ($.fn.DataTable.isDataTable('#resultsTable')) {
        $('#resultsTable').DataTable().destroy();
    }

    // Hide results container
    $('#resultsTableContainer').addClass('d-none');
    $('#resultsSummary').addClass('d-none');
    $('#noResultsFound').addClass('d-none');

    // Show initial message
    $('#noSearchPerformed').removeClass('d-none');

    // Focus on search input
    $('#amountInput').focus();
}

/**
 * Export search results to CSV
 */
function exportResults() {
    const amount = $('#amountInput').val().trim();

    if (!amount) {
        showError('Please enter a bill amount before exporting');
        return;
    }

    // Build export URL
    let url = '/groups/utilities_billing/amount_billed_search/export?amount=' + encodeURIComponent(amount);

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

        return date.toLocaleString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
}

/**
 * Format a number as currency
 * @param {number|string} value - The number to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value) {
    if (value == null) return '';

    // Parse the value to make sure it's a number
    const numValue = parseFloat(value);

    if (isNaN(numValue)) return value;

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
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
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Error:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Find the container
    const container = document.querySelector('.container');
    if (container) {
        // Insert at the top of the container
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        // If no container, add to body
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