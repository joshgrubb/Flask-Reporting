/**
 * Stock By Storeroom Report JavaScript
 * 
 * This file handles the interactive functionality for the Stock By Storeroom report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Define globally
function applyStatusFilter(filterId) {
    const table = $('#stockTable').DataTable();
    table.search('').columns().search('').draw();
    if (filterId === 'filterUnderMin') {
        table.column(7).search('Under Min').draw();
    } else if (filterId === 'filterNormal') {
        table.column(7).search('Normal').draw();
    } else if (filterId === 'filterOverMax') {
        table.column(7).search('Over Max').draw();
    }
    updateFilteredCount(table.rows({ search: 'applied' }).count());
}

function updateFilteredCount(count) {
    const storeroom = $('#storeroomSelect').val();
    const totalCount = $('#stockTable').DataTable().rows().count();
    if (count === totalCount) {
        $('#storeroomInfo').text(`Storeroom: ${storeroom}`);
    } else {
        $('#storeroomInfo').text(`Storeroom: ${storeroom} (Showing ${count} of ${totalCount} items)`);
    }
}

// Document ready function
$(document).ready(function () {
    loadData();
    $('#filterAll, #filterUnderMin, #filterNormal, #filterOverMax').click(function () {
        $('#filterAll, #filterUnderMin, #filterNormal, #filterOverMax').removeClass('active');
        $(this).addClass('active');
        applyStatusFilter($(this).attr('id'));
    });
    $('#applyFilters').click(loadData);
    $('#exportData').click(exportReportData);
});

/**
 * Load data based on selected storeroom
 */
function loadData() {
    const storeroom = $('#storeroomSelect').val();

    // Exit if no storeroom selected
    if (!storeroom) {
        showError('Please select a storeroom');
        return;
    }
    $('#filterAll, #filterUnderMin, #filterNormal, #filterOverMax').removeClass('active');
    $('#filterAll').addClass('active');

    // Show loading indicators
    $('#dataTableContainer').addClass('loading');
    $('#totalItems, #underMinItems, #normalItems, #overMaxItems').text('-');
    $('#storeroomInfo').text('Loading...');

    // Load main data
    $.ajax({
        url: '/groups/warehouse/stock_by_storeroom/data',
        data: {
            storeroom: storeroom
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDataTable(response.data);

                // Also load summary data
                loadSummaryData(storeroom);
            } else {
                showError('Error loading data: ' + response.error);
                $('#dataTableContainer').removeClass('loading');
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading data: ' + error);
            $('#dataTableContainer').removeClass('loading');
        }
    });
}

/**
 * Load summary data for the storeroom
 * @param {string} storeroom - The storeroom code
 */
function loadSummaryData(storeroom) {
    $.ajax({
        url: '/groups/warehouse/stock_by_storeroom/summary',
        data: {
            storeroom: storeroom
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                updateStats(response.data);
                initStockLevelChart(response.data);
            } else {
                showError('Error loading summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading summary data: ' + error);
        },
        complete: function () {
            $('#dataTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize DataTable with inventory data
 * @param {Array} data - The inventory data to display
 */
function initDataTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#stockTable')) {
        $('#stockTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            { data: 'STORERM' },
            {
                data: 'MINQUANTITY',
                render: function (data) {
                    return formatNumber(data, 2);
                }
            },
            {
                data: 'STOCKONHAND',
                render: function (data) {
                    return formatNumber(data, 2);
                }
            },
            {
                data: 'MAXQUANTITY',
                render: function (data) {
                    return formatNumber(data, 2);
                }
            },
            {
                data: 'Under_Min',
                render: function (data) {
                    // Format the number and add color based on value
                    const value = parseFloat(data);
                    const formattedValue = formatNumber(value, 2);

                    if (value > 0) {
                        return '<span class="text-danger">' + formattedValue + '</span>';
                    } else {
                        return '<span class="text-success">' + formattedValue + '</span>';
                    }
                }
            },
            {
                // Status column based on stock level
                data: null,
                render: function (data) {
                    const stock = parseFloat(data.STOCKONHAND) || 0;
                    const min = parseFloat(data.MINQUANTITY) || 0;
                    const max = parseFloat(data.MAXQUANTITY) || 0;

                    if (stock < min) {
                        return '<span class="badge bg-danger">Under Min</span>';
                    } else if (stock > max) {
                        return '<span class="badge bg-warning text-dark">Over Max</span>';
                    } else {
                        return '<span class="badge bg-success">Normal</span>';
                    }
                }
            }
        ],
        pageLength: 25,
        order: [[0, 'asc']], // Sort by Material ID
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        // Add row styling based on status
        createdRow: function (row, data) {
            const stock = parseFloat(data.STOCKONHAND) || 0;
            const min = parseFloat(data.MINQUANTITY) || 0;
            const max = parseFloat(data.MAXQUANTITY) || 0;

            if (stock < min) {
                $(row).addClass('table-danger');
            } else if (stock > max) {
                $(row).addClass('table-warning');
            } else {
                $(row).addClass('table-success');
            }
        }
    };

    // Initialize DataTable
    const table = $('#stockTable').DataTable(dataTableOptions);

    const activeFilterId = $('.btn-group button.active').attr('id');
    if (activeFilterId && activeFilterId !== 'filterAll') {
        // Re-apply the active filter after redrawing
        setTimeout(() => {
            applyStatusFilter(activeFilterId);
        }, 100);
    }

    // Add this event handler to the DataTable
    table.on('draw', function () {
        const visibleRows = table.rows({ search: 'applied' }).count();
        updateFilteredCount(visibleRows);
    });

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Update summary statistics on the page
 * @param {Object} data - The summary data
 */
function updateStats(data) {
    if (!data) {
        return;
    }

    // Update stats cards
    $('#totalItems').text(data.TotalItems || 0);
    $('#underMinItems').text(data.UnderMinCount || 0);
    $('#normalItems').text(data.NormalCount || 0);
    $('#overMaxItems').text(data.OverMaxCount || 0);

    // Update storeroom info
    const storeroom = $('#storeroomSelect').val();
    $('#storeroomInfo').text(`Storeroom: ${storeroom}`);
}

/**
 * Initialize the stock level distribution chart
 * @param {Object} data - The summary data
 */
function initStockLevelChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        return;
    }

    // Get the chart canvas
    const canvas = document.getElementById('stockLevelChart');
    if (!canvas) {
        console.error('Cannot find stockLevelChart canvas element');
        return;
    }

    // Destroy existing chart if it exists
    let existingChart;
    try {
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.warn('No existing chart found or error checking:', e);
    }

    // Extract the status counts
    const underMin = data.UnderMinCount || 0;
    const normal = data.NormalCount || 0;
    const overMax = data.OverMaxCount || 0;

    // Create a pie chart
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: ['Under Minimum', 'Normal Range', 'Over Maximum'],
            datasets: [{
                data: [underMin, normal, overMax],
                backgroundColor: [
                    'rgba(211, 47, 47, 0.7)',  // Red for under min
                    'rgba(46, 125, 50, 0.7)',  // Green for normal
                    'rgba(255, 152, 0, 0.7)'   // Orange for over max
                ],
                borderColor: [
                    'rgba(211, 47, 47, 1)',    // Red for under min
                    'rgba(46, 125, 50, 1)',    // Green for normal
                    'rgba(255, 152, 0, 1)'     // Orange for over max
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = data.TotalItems || 0;
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    const storeroom = $('#storeroomSelect').val();

    // Build export URL
    let url = '/groups/warehouse/stock_by_storeroom/export';
    url += `?storeroom=${encodeURIComponent(storeroom)}`;

    // Open in new tab/window
    window.open(url, '_blank');
}

/**
 * Format a number with comma separators and fixed decimal places
 * @param {number|string} value - The number to format
 * @param {number} decimals - Number of decimal places to show
 * @returns {string} - Formatted number string
 */
function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || value === '') {
        return '0';
    }

    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
        return '0';
    }

    return numValue.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
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