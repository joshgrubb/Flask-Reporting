/**
 * Cycle Info Report JavaScript
 * 
 * This file handles the interactive functionality for the Cycle Info report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize multiselect for cycles if library is available
    if ($.fn.multiselect) {
        $('#cycleSelect').multiselect({
            includeSelectAllOption: true,
            nonSelectedText: 'All Cycles',
            enableFiltering: true
        });
    }

    // Initial data load
    loadAllData();

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Reset cycles to nothing selected (which means all)
        if ($.fn.multiselect) {
            $('#cycleSelect').multiselect('deselectAll', false);
            $('#cycleSelect').multiselect('updateButtonText');
        } else {
            $('#cycleSelect').val([]);
        }

        // Reload data
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
    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#chartContainer').addClass('loading');
    $('#totalAccounts, #emailCoverage, #cycleCount').text('-');

    // Get filter values
    const selectedCycles = $('#cycleSelect').val() || [];
    const cycleParam = selectedCycles.join(',');

    // Prepare filter params
    const filterParams = {};
    if (cycleParam) filterParams.cycles = cycleParam;

    // Load main data
    $.ajax({
        url: '/groups/utilities_billing/cycle_info/data',
        data: filterParams,
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);
                updateBasicStats(response.data, selectedCycles);
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

    // Load summary data for charts
    $.ajax({
        url: '/groups/utilities_billing/cycle_info/summary',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initCycleChart(response.data, selectedCycles);
            } else {
                showError('Error loading summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading summary data: ' + error);
        },
        complete: function () {
            $('#chartContainer').removeClass('loading');
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
            { data: 'FormalName' },
            {
                data: 'EmailAddress',
                render: function (data) {
                    return data || '<span class="text-muted">No email</span>';
                }
            },
            { data: 'FullAddress' },
            {
                data: 'Cycle',
                render: function (data) {
                    return `<span class="badge bg-primary">${data}</span>`;
                }
            }
        ],
        pageLength: 25,
        order: [[4, 'asc'], [0, 'asc']], // Sort by Cycle, then Account Number
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
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
 * Initialize the cycle chart
 * @param {Array} data - The summary data for cycles
 * @param {Array} selectedCycles - The user-selected cycles
 */
function initCycleChart(data, selectedCycles) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('cycleChart');
    if (!canvas) {
        console.error('Cannot find cycleChart canvas element');
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

    // Filter data if cycles are selected
    let chartData = data;
    if (selectedCycles && selectedCycles.length > 0) {
        chartData = data.filter(item => selectedCycles.includes(item.Cycle));
    }

    // Prepare data for chart
    const labels = chartData.map(item => item.Cycle);
    const accountCounts = chartData.map(item => item.AccountCount);
    const emailCounts = chartData.map(item => item.EmailCount);

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
                        label: 'Total Accounts',
                        data: accountCounts,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'With Email',
                        data: emailCounts,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
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
                                    return `${label}: ${value}`;
                                } else {
                                    // For email dataset, add percentage
                                    const totalAccounts = accountCounts[context.dataIndex];
                                    const percentage = totalAccounts > 0 ? Math.round((value / totalAccounts) * 100) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
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
                        beginAtZero: true,
                        grid: {
                            color: gridColor
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

    // Update email coverage statistics
    updateEmailStats(chartData);
}

/**
 * Update basic statistics
 * @param {Array} data - The report data
 * @param {Array} selectedCycles - The user-selected cycles
 */
function updateBasicStats(data, selectedCycles) {
    if (!data || !data.length) {
        $('#totalAccounts').text('0');
        return;
    }

    // Count total accounts
    const totalAccounts = data.length;
    $('#totalAccounts').text(totalAccounts);

    // Update cycle filter info
    if (selectedCycles && selectedCycles.length > 0) {
        $('#cycleFilterInfo').text(`Filtered by selected cycles`);
        $('#cycleCount').text(selectedCycles.length);
        $('#cyclesList').text(selectedCycles.join(', '));
    } else {
        $('#cycleFilterInfo').text(`All cycles included`);

        // Get unique cycles from data
        const uniqueCycles = [...new Set(data.map(item => item.Cycle))];
        $('#cycleCount').text(uniqueCycles.length);
        $('#cyclesList').text('All cycles');
    }
}

/**
 * Update email statistics based on summary data
 * @param {Array} data - The summary data
 */
function updateEmailStats(data) {
    if (!data || !data.length) {
        $('#emailCoverage').text('0%');
        $('#emailCount').text('No email addresses found');
        return;
    }

    // Calculate overall email coverage
    let totalAccounts = 0;
    let totalEmailAddresses = 0;

    data.forEach(item => {
        totalAccounts += item.AccountCount;
        totalEmailAddresses += item.EmailCount;
    });

    const coveragePercentage = totalAccounts > 0 ? Math.round((totalEmailAddresses / totalAccounts) * 100) : 0;
    $('#emailCoverage').text(`${coveragePercentage}%`);
    $('#emailCount').text(`${totalEmailAddresses} of ${totalAccounts} accounts`);
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Get filter values
    const selectedCycles = $('#cycleSelect').val() || [];
    const cycleParam = selectedCycles.join(',');

    // Build export URL with query parameters
    let url = '/groups/utilities_billing/cycle_info/export';

    if (cycleParam) {
        url += `?cycles=${encodeURIComponent(cycleParam)}`;
    }

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