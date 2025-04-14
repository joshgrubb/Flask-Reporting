/**
 * High Balance Report JavaScript
 * 
 * This file handles the interactive functionality for the High Balance report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize Select2 for account types
    if ($.fn.select2) {
        $('#accountTypeSelect').select2({
            placeholder: 'Select account types',
            allowClear: true,
            closeOnSelect: false,
            width: '100%'
        });
    } else {
        console.warn('Select2 library not loaded. Falling back to standard select.');
    }

    // Initial data load
    loadAllData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Reset balance to default
        $('#balanceInput').val(100);

        // Reset account types to residential only
        if ($.fn.select2) {
            $('#accountTypeSelect').val(['477']).trigger('change');
        } else {
            $('#accountTypeSelect option').prop('selected', false);
            $('#accountTypeSelect option[value="477"]').prop('selected', true);
        }

        // Reload data
        loadAllData();
    });

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Reset balance to default
        $('#balanceInput').val(100);

        // Reset account types to residential only
        $('#accountTypeSelect option').prop('selected', false);
        $('#accountTypeSelect option[value="477"]').prop('selected', true);

        // Reload data
        loadAllData();
    });

    /**
 * Load all data for the report
 */
    function loadAllData() {
        // Show loading indicators
        $('#dataTableContainer').addClass('loading');
        $('#totalAccounts, #totalBalance, #avgBalance, #maxBalance').text('-');
        $('#balanceThresholdInfo').text('Loading...');

        // Get filter values
        const balanceThreshold = $('#balanceInput').val() || 100;

        // Get selected account types
        let selectedAccountTypes;
        if ($.fn.select2) {
            selectedAccountTypes = $('#accountTypeSelect').val() || [];
        } else {
            selectedAccountTypes = Array.from($('#accountTypeSelect option:selected')).map(option => option.value);
        }

        // Default to residential if nothing selected
        if (!selectedAccountTypes.length) {
            selectedAccountTypes = ['477'];
        }

        // Join for parameter string
        const accountTypesParam = selectedAccountTypes.join(',');

        // Prepare filter params
        const filterParams = {
            balance: balanceThreshold,
            account_types: accountTypesParam
        };

        // Load main data
        $.ajax({
            url: '/groups/utilities_billing/high_balance/data',
            data: filterParams,
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    initDataTable(response.data);
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
            url: '/groups/utilities_billing/high_balance/summary',
            data: filterParams,
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    updateSummaryStats(response.data);
                    initDistributionChart(response.data);
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
                    data: 'Balance',
                    render: function (data) {
                        // Format balance as currency
                        return formatCurrency(data);
                    }
                },
                { data: 'AccountType' },
                { data: 'FullAddress' },
                { data: 'LastName' },
                { data: 'FirstName' },
                {
                    data: 'EmailAddress',
                    render: function (data) {
                        return data || '<span class="text-muted">None</span>';
                    }
                },
                {
                    data: 'PrimaryPhone',
                    render: function (data) {
                        return data || '<span class="text-muted">None</span>';
                    }
                }
            ],
            pageLength: 25,
            order: [[1, 'desc']], // Sort by Balance, highest first
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            },
            rowCallback: function (row, data) {
                // Add classes based on balance
                if (data.Balance >= 1000) {
                    $(row).addClass('table-danger');
                } else if (data.Balance >= 500) {
                    $(row).addClass('table-warning');
                }
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
     * Initialize the balance distribution chart
     * @param {Array} data - The summary data for account types
     */
    function initDistributionChart(data) {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded properly');
            showError('Chart.js library failed to load. Please check console for details.');
            return;
        }

        // Get canvas element
        const canvas = document.getElementById('balanceDistributionChart');
        if (!canvas) {
            console.error('Cannot find balanceDistributionChart canvas element');
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
        const labels = data.map(item => item.AccountType || 'Unknown');
        const values = data.map(item => parseFloat(item.TotalBalance) || 0);
        const accountCounts = data.map(item => item.TotalAccounts || 0);

        // Create color palette
        const colors = [
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(201, 203, 207, 0.7)'
        ];

        // Determine if dark mode is active
        const isDarkMode = document.documentElement.classList.contains('dark-mode');

        // Define chart colors based on mode
        const textColor = isDarkMode ? '#E0E0E0' : '#333333';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

        // Create new chart
        try {
            new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Total Balance',
                            data: values,
                            backgroundColor: colors,
                            borderColor: colors.map(color => color.replace('0.7', '1')),
                            borderWidth: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Number of Accounts',
                            data: accountCounts,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1,
                            type: 'line',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: textColor
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.dataset.label || '';
                                    const value = context.raw || 0;

                                    if (context.datasetIndex === 0) {
                                        return `${label}: ${formatCurrency(value)}`;
                                    } else {
                                        return `${label}: ${value}`;
                                    }
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
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                callback: function (value) {
                                    return formatCurrency(value);
                                },
                                color: textColor
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            grid: {
                                drawOnChartArea: false
                            },
                            ticks: {
                                precision: 0,
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
     * Update summary statistics
     * @param {Array} data - The summary data
     */
    function updateSummaryStats(data) {
        if (!data || !data.length) {
            $('#totalAccounts').text('0');
            $('#totalBalance').text('$0.00');
            $('#avgBalance').text('$0.00');
            $('#maxBalance').text('$0.00');
            return;
        }

        // Calculate totals across all account types
        let totalAccounts = 0;
        let totalBalance = 0;
        let maxBalance = 0;

        data.forEach(item => {
            totalAccounts += parseInt(item.TotalAccounts || 0);
            totalBalance += parseFloat(item.TotalBalance || 0);

            const itemMaxBalance = parseFloat(item.MaxBalance || 0);
            if (itemMaxBalance > maxBalance) {
                maxBalance = itemMaxBalance;
            }
        });

        // Calculate average
        const avgBalance = totalAccounts > 0 ? totalBalance / totalAccounts : 0;

        // Update the stats displays
        $('#totalAccounts').text(totalAccounts);
        $('#totalBalance').text(formatCurrency(totalBalance));
        $('#avgBalance').text(formatCurrency(avgBalance));
        $('#maxBalance').text(formatCurrency(maxBalance));

        // Update threshold info
        const balanceThreshold = $('#balanceInput').val() || 100;
        $('#balanceThresholdInfo').text(`Above $${balanceThreshold} threshold`);
    }

    /**
     * Export report data to CSV
     */
    function exportReportData() {
        // Get filter values
        const balanceThreshold = $('#balanceInput').val() || 100;
        const selectedAccountTypes = $('#accountTypeSelect').val() || ['477'];
        const accountTypesParam = selectedAccountTypes.join(',');

        // Build export URL with query parameters
        let url = '/groups/utilities_billing/high_balance/export';
        url += `?balance=${encodeURIComponent(balanceThreshold)}`;
        url += `&account_types=${encodeURIComponent(accountTypesParam)}`;

        // Open in new tab/window
        window.open(url, '_blank');
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
})