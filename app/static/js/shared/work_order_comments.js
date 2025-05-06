/**
 * Work Order Comments Search Report JavaScript
 * 
 * This file handles the interactive functionality for the Work Order Comments Search report,
 * including search functionality, table initialization, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker if available
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Set up form submission handler
    $('#searchForm').on('submit', function (e) {
        e.preventDefault();
        searchComments();
    });

    // Reset button handler
    $('#resetButton').click(function () {
        // Clear search term
        $('#searchTermInput').val('');

        // Reset to default dates (last 30 days)
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 30);
        const formattedStartDate = startDate.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(endDate);

        // Hide results sections
        $('#resultsSummary').hide();
        $('#resultsSection').hide();
        $('#noResultsMessage').hide();
        $('#initialInstructions').show();

        // Disable export button
        $('#exportData').prop('disabled', true);
    });

    // Export button handler
    $('#exportData').click(function () {
        exportSearchResults();
    });
});

/**
 * Search for comments containing the specified search term
 */
function searchComments() {
    // Get search parameters
    const searchTerm = $('#searchTermInput').val();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Validate search term
    if (!searchTerm || searchTerm.length < 2) {
        showError('Search term must be at least 2 characters long');
        return;
    }

    // Show loading indicator on the table container
    $('#commentsTableContainer').addClass('loading');

    // Hide initial instructions and show results section (will be populated after search)
    $('#initialInstructions').hide();
    $('#noResultsMessage').hide();
    $('#resultsSummary').show();
    $('#resultsSection').show();

    // Update search term and date range info
    $('#searchTermInfo').text(`Search term: "${searchTerm}"`);
    $('#dateRange').text(`${formatDate(startDate)} to ${formatDate(endDate)}`);

    // Call the API to search for comments
    $.ajax({
        url: `/groups/${getCurrentGroup()}/work_order_comments/search`,
        data: {
            search_term: searchTerm,
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Update results count
                $('#totalResults').text(response.count);

                // If we got results, display them in the table
                if (response.count > 0) {
                    // Initialize the data table with search results
                    initCommentsTable(response.data);

                    // Show the results section and enable export button
                    $('#resultsSection').show();
                    $('#noResultsMessage').hide();
                    $('#exportData').prop('disabled', false);
                } else {
                    // No results found
                    $('#resultsSection').hide();
                    $('#noResultsMessage').show();
                    $('#exportData').prop('disabled', true);
                }
            } else {
                showError('Error searching comments: ' + response.error);
                $('#resultsSection').hide();
                $('#exportData').prop('disabled', true);
            }
        },
        error: function (xhr, status, error) {
            let errorMessage = 'Error searching comments';

            // Try to extract more specific error from response
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMessage += ': ' + response.error;
                }
            } catch (e) {
                errorMessage += ': ' + error;
            }

            showError(errorMessage);
            $('#resultsSection').hide();
            $('#exportData').prop('disabled', true);
        },
        complete: function () {
            // Remove loading indicator
            $('#commentsTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the comments data table
 * @param {Array} data - The comments data
 */
function initCommentsTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#commentsTable')) {
        $('#commentsTable').DataTable().destroy();
    }

    // Initialize DataTable
    const table = $('#commentsTable').DataTable({
        data: data,
        columns: [
            {
                data: 'WORKORDERID',
                render: function (data) {
                    // Link directly to the work order details page
                    const currentGroup = getCurrentGroup();
                    const url = `/groups/${currentGroup}/work_orders/${data}`;
                    return `<a href="${url}" class="work-order-link">${data}</a>`;
                }
            },
            { data: 'DESCRIPTION' },
            { data: 'STATUS' },
            { data: 'AUTHOR_NAME' },
            {
                data: 'COMMENTS',
                render: function (data, type, row) {
                    // For display, highlight the search term within the comment
                    if (type === 'display') {
                        const searchTerm = $('#searchTermInput').val();
                        if (searchTerm && data) {
                            // Escape search term for regex and create highlight pattern
                            const escSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                            const regex = new RegExp(`(${escSearchTerm})`, 'gi');
                            return data.replace(regex, '<span class="highlight">$1</span>');
                        }
                    }
                    return data;
                }
            },
            {
                data: 'DATECREATED',
                render: function (data) {
                    return formatDate(data);
                }
            }
        ],
        pageLength: 25,
        order: [[5, 'desc']], // Sort by date created, newest first
        language: {
            search: "Filter results:",
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
 * Export search results to CSV
 */
function exportSearchResults() {
    // Get search parameters
    const searchTerm = $('#searchTermInput').val();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Validate search term
    if (!searchTerm || searchTerm.length < 2) {
        showError('Search term must be at least 2 characters long');
        return;
    }

    // Build export URL
    let url = `/groups/${getCurrentGroup()}/work_order_comments/export`;
    let params = [];

    if (searchTerm) params.push(`search_term=${encodeURIComponent(searchTerm)}`);
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Format a date string for display
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
 * Get the current group from the URL path
 * Used to build the correct URL for API calls
 * @returns {string} - The current group name
 */
function getCurrentGroup() {
    // Extract group from URL path
    const pathParts = window.location.pathname.split('/');
    const groupsIndex = pathParts.indexOf('groups');

    if (groupsIndex !== -1 && pathParts.length > groupsIndex + 1) {
        return pathParts[groupsIndex + 1];
    }

    // Default fallback
    return 'water_resources';
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

    /**
     * Add CSS styles needed for this report
     */
    function addStyles() {
        // Create style element if it doesn't exist
        if (!document.getElementById('work-order-comments-styles')) {
            const style = document.createElement('style');
            style.id = 'work-order-comments-styles';
            style.textContent = `
            .highlight {
                background-color: rgba(255, 193, 7, 0.3);
                padding: 0 2px;
                border-radius: 2px;
                font-weight: bold;
            }
            
            .work-order-link {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 500;
            }
            
            .work-order-link:hover {
                text-decoration: underline;
            }
        `;
            document.head.appendChild(style);
        }
    }

    // Add the styles when the document is ready
    $(document).ready(addStyles);
}