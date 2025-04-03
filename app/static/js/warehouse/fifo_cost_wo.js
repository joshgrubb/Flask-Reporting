/**
 * FIFO Work Order Cost Report JavaScript
 * 
 * This file handles the interactive functionality for the FIFO Work Order Cost report,
 * including loading data, initializing tables, charts and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker if available
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initial data load
    loadWorkOrderData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadWorkOrderData();
    });

    $('#resetFilters').click(function () {
        // Reset to default dates (last complete calendar month)
        const today = new Date();

        // Get the first day of the current month
        const firstDayCurrentMonth = new Date(today.getFullYear(), today.getMonth(), 1);

        // Get the last day of the previous month
        const lastDayPrevMonth = new Date(firstDayCurrentMonth);
        lastDayPrevMonth.setDate(lastDayPrevMonth.getDate() - 1);

        // Get the first day of the previous month
        const firstDayPrevMonth = new Date(lastDayPrevMonth.getFullYear(), lastDayPrevMonth.getMonth(), 1);

        // Format dates for input fields
        const formattedStartDate = firstDayPrevMonth.toISOString().slice(0, 10);
        const formattedEndDate = lastDayPrevMonth.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(formattedEndDate);

        // Load data with reset filters
        loadWorkOrderData();
    });

    $('#exportData').click(function () {
        exportReportData();
    });
});

/**
 * Load work order data based on filters
 */
function loadWorkOrderData() {
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalWorkOrders, #totalCost, #averageCost').text('-');
    $('#dateRangeInfo').text('Loading...');

    // Load main data
    $.ajax({
        url: '/groups/warehouse/fifo_cost_wo/data',
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

    // Load summary data
    $.ajax({
        url: '/groups/warehouse/fifo_cost_wo/summary',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Additional summary visualizations could be added here
                console.log('Summary data:', response.data);
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
 * Initialize DataTable with work order data
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
            { data: 'WORKORDERID' },
            {
                data: 'TRANSDATE',
                render: function (data) {
                    return formatDate(data);
                }
            },
            { data: 'WOCATEGORY' },
            {
                data: null,
                render: function (data) {
                    // Create a description from the first item
                    if (data.ITEMS && data.ITEMS.length > 0) {
                        return data.ITEMS[0].DESCRIPTION || 'N/A';
                    }
                    return 'N/A';
                }
            },
            {
                data: null,
                render: function (data) {
                    // Show count of items
                    if (data.ITEMS) {
                        return `${data.ITEMS.length} item(s)`;
                    }
                    return '0 items';
                }
            },
            {
                data: 'TOTAL_COST',
                render: function (data) {
                    return formatCurrency(data);
                }
            }
        ],
        pageLength: 10,
        order: [[1, 'desc']], // Sort by date, newest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        // Add row expansion callback to show item details
        rowCallback: function (row, data) {
            $(row).on('click', function () {
                // Create and show a detailed view of items
                showWorkOrderDetails(data);
            });
            $(row).css('cursor', 'pointer');
        }
    };

    // Initialize DataTable
    const table = $('#workOrdersTable').DataTable(dataTableOptions);

    // Handle window resize
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Show work order details in a modal
 * @param {Object} workOrder - The work order data
 */
function showWorkOrderDetails(workOrder) {
    // Check if modal already exists, if not create it
    let modalElement = $('#workOrderDetailsModal');
    if (modalElement.length === 0) {
        // Create modal HTML
        const modalHTML = `
        <div class="modal fade" id="workOrderDetailsModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Work Order Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Work Order ID:</strong> <span id="detail-workorder-id"></span>
                            </div>
                            <div class="col-md-6">
                                <strong>Date:</strong> <span id="detail-date"></span>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Category:</strong> <span id="detail-category"></span>
                            </div>
                            <div class="col-md-6">
                                <strong>Total Cost:</strong> <span id="detail-total-cost"></span>
                            </div>
                        </div>
                        <h6>Items</h6>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Material ID</th>
                                    <th>Description</th>
                                    <th>Units</th>
                                    <th>Cost</th>
                                </tr>
                            </thead>
                            <tbody id="detail-items-tbody">
                            </tbody>
                        </table>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Add modal to page
        $('body').append(modalHTML);
        modalElement = $('#workOrderDetailsModal');
    }

    // Fill in the modal with work order details
    $('#detail-workorder-id').text(workOrder.WORKORDERID);
    $('#detail-date').text(formatDate(workOrder.TRANSDATE));
    $('#detail-category').text(workOrder.WOCATEGORY);
    $('#detail-total-cost').text(formatCurrency(workOrder.TOTAL_COST));

    // Clear and populate items table
    const itemsBody = $('#detail-items-tbody');
    itemsBody.empty();

    if (workOrder.ITEMS && workOrder.ITEMS.length > 0) {
        workOrder.ITEMS.forEach(item => {
            const row = `
            <tr>
                <td>${item.MATERIALUID || 'N/A'}</td>
                <td>${item.DESCRIPTION || 'N/A'}</td>
                <td>${item.UNITSREQUIRED || '1'}</td>
                <td>${formatCurrency(item.COST)}</td>
            </tr>
            `;
            itemsBody.append(row);
        });
    } else {
        itemsBody.append('<tr><td colspan="4" class="text-center">No items found</td></tr>');
    }

    // Show the modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

/**
 * Update statistics based on data
 * @param {Array} data - The work order data
 */
function updateStats(data) {
    if (!data || !data.length) {
        $('#totalWorkOrders').text('0');
        $('#totalCost').text('$0.00');
        $('#averageCost').text('$0.00');
        $('#dateRangeInfo').text('No data available');
        return;
    }

    // Calculate total work orders
    const totalWorkOrders = data.length;
    $('#totalWorkOrders').text(totalWorkOrders);

    // Calculate total cost
    const totalCost = data.reduce((sum, wo) => sum + (parseFloat(wo.TOTAL_COST) || 0), 0);
    $('#totalCost').text(formatCurrency(totalCost));

    // Calculate average cost
    const avgCost = totalCost / totalWorkOrders;
    $('#averageCost').text(formatCurrency(avgCost));

    // Date range info
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    $('#dateRangeInfo').text(`${formatDate(startDate)} to ${formatDate(endDate)}`);
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
 * Export report data to CSV
 */
function exportReportData() {
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Build export URL
    let url = '/groups/warehouse/fifo_cost_wo/export';
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