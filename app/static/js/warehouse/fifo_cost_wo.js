/**
 * FIFO Cost by Account Number Report JavaScript
 * 
 * This file handles the interactive functionality for the FIFO Cost by Account report,
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
    loadAccountData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadAccountData();
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
        loadAccountData();
    });

    // Handle the export dropdown options
    $('#exportDetail').click(function () {
        exportReportData('detail');
    });

    $('#exportSummary').click(function () {
        exportReportData('summary');
    });

    /**
     * Load account data based on filters
     */
    function loadAccountData() {
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();

        // Show loading indicators
        $('#dataTableContainer').addClass('loading');
        $('#totalAccounts, #totalCost, #missingAccountsCost').text('-');
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

        // Remove any existing event listeners to prevent duplicates
        $('#accountsTable tbody').off('click', 'button.view-details');

        // Create options object for DataTable
        const dataTableOptions = {
            data: data,
            columns: [
                {
                    data: 'ACCTNUM',
                    render: function (data, type, row) {
                        if (row.IS_MISSING) {
                            return '<span class="badge bg-danger">MISSING</span>';
                        }
                        return data;
                    }
                },
                { data: 'ITEM_COUNT' },
                { data: 'WORK_ORDER_COUNT' },
                {
                    data: 'TOTAL_COST',
                    render: function (data) {
                        return formatCurrency(data);
                    }
                },
                {
                    data: null,
                    orderable: false,
                    render: function () {
                        return '<button class="btn btn-sm btn-primary view-details">View Details</button>';
                    }
                }
            ],
            pageLength: 25,
            order: [[0, 'desc']], // Sort by account number, with missing at top due to sorting in backend
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            },
            // Row styling
            createdRow: function (row, data) {
                if (data.IS_MISSING) {
                    $(row).addClass('table-danger');
                }
            }
        };

        // Initialize DataTable
        const table = $('#accountsTable').DataTable(dataTableOptions);

        // Add event listener for the view details button AFTER the table is initialized
        $('#accountsTable tbody').on('click', 'button.view-details', function () {
            const data = table.row($(this).parents('tr')).data();
            showAccountDetails(data);
        });

        // Handle window resize
        $(window).on('resize', function () {
            if (table && typeof table.columns === 'function') {
                table.columns.adjust();
            }
        });
    }

    /**
     * Show account details in a modal
     * @param {Object} account - The account data
     */
    function showAccountDetails(account) {
        // Remove any existing modal to prevent duplication issues
        $('#accountDetailsModal').remove();

        // Create modal HTML
        const modalHTML = `
    <div class="modal fade" id="accountDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        GL Account Details: <span id="detail-account-id"></span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <strong>Items:</strong> <span id="detail-item-count"></span>
                        </div>
                        <div class="col-md-4">
                            <strong>Work Orders:</strong> <span id="detail-wo-count"></span>
                        </div>
                        <div class="col-md-4">
                            <strong>Total Cost:</strong> <span id="detail-total-cost"></span>
                        </div>
                    </div>
                    <h6>Items in this Account</h6>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Work Order ID</th>
                                    <th>Category</th>
                                    <th>Date</th>
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

        // Get the modal element
        const modalElement = $('#accountDetailsModal');

        // Apply dark mode to modal if active
        if (document.documentElement.classList.contains('dark-mode')) {
            modalElement.find('.modal-content').addClass('bg-dark text-light');
            modalElement.find('.modal-header, .modal-footer').addClass('border-secondary');
            modalElement.find('.table').addClass('table-dark');
        }

        // Fill in the modal with account details
        let accountLabel = account.ACCTNUM;
        if (account.IS_MISSING) {
            accountLabel = '<span class="badge bg-danger">MISSING ACCOUNT NUMBER</span>';
        }

        $('#detail-account-id').html(accountLabel);
        $('#detail-item-count').text(account.ITEM_COUNT);
        $('#detail-wo-count').text(account.WORK_ORDER_COUNT);
        $('#detail-total-cost').text(formatCurrency(account.TOTAL_COST));

        // Clear and populate items table
        const itemsBody = $('#detail-items-tbody');
        itemsBody.empty();

        if (account.ITEMS && account.ITEMS.length > 0) {
            // Sort items by work order and date
            const sortedItems = [...account.ITEMS].sort((a, b) => {
                // First sort by work order ID
                if (a.WORKORDERID !== b.WORKORDERID) {
                    return a.WORKORDERID.localeCompare(b.WORKORDERID);
                }
                // Then by date if same work order
                return new Date(a.TRANSDATE) - new Date(b.TRANSDATE);
            });

            sortedItems.forEach(item => {
                const row = `
            <tr>
                <td>${item.WORKORDERID}</td>
                <td>${item.WOCATEGORY}</td>
                <td>${formatDate(item.TRANSDATE)}</td>
                <td>${item.MATERIALUID || 'N/A'}</td>
                <td>${item.DESCRIPTION || 'N/A'}</td>
                <td>${item.UNITSREQUIRED || '1'}</td>
                <td>${formatCurrency(item.COST)}</td>
            </tr>
            `;
                itemsBody.append(row);
            });
        } else {
            itemsBody.append('<tr><td colspan="7" class="text-center">No items found</td></tr>');
        }

        // Show the modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }

    /**
     * Update statistics based on data
     * @param {Array} data - The account data
     */
    function updateStats(data) {
        if (!data || !data.length) {
            $('#totalAccounts').text('0');
            $('#totalCost').text('$0.00');
            $('#missingAccountsCost').text('$0.00');
            $('#dateRangeInfo').text('No data available');
            return;
        }

        // Calculate total accounts
        const totalAccounts = data.length;
        $('#totalAccounts').text(totalAccounts);

        // Calculate total cost across all accounts
        const totalCost = data.reduce((sum, acct) => sum + (parseFloat(acct.TOTAL_COST) || 0), 0);
        $('#totalCost').text(formatCurrency(totalCost));

        // Calculate cost of items with missing accounts
        const missingAccounts = data.find(acct => acct.IS_MISSING);
        const missingCost = missingAccounts ? missingAccounts.TOTAL_COST : 0;
        $('#missingAccountsCost').text(formatCurrency(missingCost));

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
     * @param {string} type - Type of export ('detail' or 'summary')
     */
    function exportReportData(type = 'detail') {
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();

        // Build export URL
        let url = '/groups/warehouse/fifo_cost_wo/export';
        url += `?start_date=${startDate}&end_date=${endDate}&type=${type}`;

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
});