/**
 * FIFO Stock Cost Report JavaScript
 * 
 * This file handles the interactive functionality for the FIFO Stock Cost report,
 * including loading data, initializing charts, tables, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Load available categories
    loadCategories();

    // Event handlers
    $('#applyFilters').click(function () {
        const selectedCategory = $('#categorySelect').val();
        if (selectedCategory) {
            loadInventoryData(selectedCategory);
            $('#exportDropdown').prop('disabled', false);
        } else {
            showError('Please select a category');
            $('#exportDropdown').prop('disabled', true);
        }
    });

    // Handle the export dropdown options
    $('#exportDetail').click(function () {
        exportReportData('detail');
    });

    $('#exportSummary').click(function () {
        exportReportData('summary');
    });
});

/**
 * Load available categories for the dropdown
 */
function loadCategories() {
    $.ajax({
        url: '/groups/warehouse/fifo_stock/categories',
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                populateCategoryDropdown(response.data);
            } else {
                showError('Error loading categories: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading categories: ' + error);
        }
    });
}

/**
 * Populate the category dropdown with options
 * @param {Array} categories - Array of category names
 */
function populateCategoryDropdown(categories) {
    const dropdown = $('#categorySelect');

    // Clear existing options except the first one
    dropdown.find('option:not(:first)').remove();

    // Add categories as options
    categories.forEach(category => {
        dropdown.append($('<option></option>').val(category).text(category));
    });
}

/**
 * Load inventory data for the selected category
 * @param {string} category - The selected category
 */
function loadInventoryData(category) {
    // Show loading indicators and hide results sections
    $('#dataTableContainer, #summaryTableContainer').addClass('loading');
    $('#initialMessage').hide();
    $('#summaryStats, #chartsSection, #detailedDataSection, #summaryDataSection').hide();

    // Load detailed inventory data
    $.ajax({
        url: '/groups/warehouse/fifo_stock/data',
        data: { category: category },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Show detailed data section
                $('#detailedDataSection').show();
                initDetailedTable(response.data);
            } else {
                showError('Error loading inventory data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading inventory data: ' + error);
        },
        complete: function () {
            $('#dataTableContainer').removeClass('loading');
        }
    });

    // Load summary data
    $.ajax({
        url: '/groups/warehouse/fifo_stock/summary',
        data: { category: category },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Show summary sections
                $('#summaryStats, #chartsSection, #summaryDataSection').show();

                // Initialize summary table and charts
                initSummaryTable(response.data);
                initCharts(response.data);

                // Update summary statistics
                updateSummaryStats(response.data, response.category, response.totalValue, response.totalQuantity);
            } else {
                showError('Error loading summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading summary data: ' + error);
        },
        complete: function () {
            $('#summaryTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the detailed inventory table
 * @param {Array} data - The inventory data
 */
function initDetailedTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#inventoryTable')) {
        $('#inventoryTable').DataTable().destroy();
    }

    // Process data to add calculated value
    const processedData = data.map(item => {
        const quantity = parseFloat(item.QUANTITY) || 0;
        const unitCost = parseFloat(item.UNITCOST) || 0;
        const value = quantity * unitCost;

        return {
            ...item,
            Value: value
        };
    });

    // Create options object for DataTable
    const dataTableOptions = {
        data: processedData,
        columns: [
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            {
                data: 'QUANTITY',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                data: 'UNITCOST',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'Value',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'PURCHASEDATE',
                render: function (data) {
                    return formatDate(data);
                }
            },
        ],
        pageLength: 25,
        order: [[0, 'asc'], [5, 'asc']], // Sort by Material ID, then Purchase Date
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#inventoryTable').DataTable(dataTableOptions);

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize the summary table
 * @param {Array} data - The summary data
 */
function initSummaryTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#summaryTable')) {
        $('#summaryTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            {
                data: 'TotalQuantity',
                render: function (data) {
                    return parseFloat(data).toFixed(2);
                }
            },
            {
                data: 'AvgUnitCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'TotalValue',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'OldestPurchaseDate',
                render: function (data) {
                    return formatDate(data);
                }
            },
            {
                data: 'NewestPurchaseDate',
                render: function (data) {
                    return formatDate(data);
                }
            },
        ],
        pageLength: 10,
        order: [[4, 'desc']], // Sort by Total Value, highest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        }
    };

    // Initialize DataTable
    const table = $('#summaryTable').DataTable(dataTableOptions);

    // Window resize handler
    $(window).on('resize', function () {
        if (table && typeof table.columns === 'function') {
            table.columns.adjust();
        }
    });
}

/**
 * Initialize charts for visualization
 * @param {Array} data - The summary data
 */
function initCharts(data) {
    // Only show top 10 items for the charts
    const topItems = [...data].sort((a, b) => b.TotalValue - a.TotalValue).slice(0, 10);

    // Prepare data for charts
    const labels = topItems.map(item => {
        // Truncate long descriptions
        const desc = item.DESCRIPTION;
        return desc.length > 20 ? desc.substring(0, 20) + '...' : desc;
    });

    const valueData = topItems.map(item => parseFloat(item.TotalValue));
    const quantityData = topItems.map(item => parseFloat(item.TotalQuantity));

    // Create value distribution chart
    createPieChart('valueDistributionChart', 'Value Distribution', labels, valueData);

    // Create quantity distribution chart
    createBarChart('quantityDistributionChart', 'Quantity Distribution', labels, quantityData);
}

/**
 * Create a pie chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - The chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 */
/**
 * Create a bar chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - The chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 */
function createBarChart(canvasId, title, labels, data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Cannot find ${canvasId} canvas element`);
        return;
    }

    // Safely destroy existing chart if it exists
    let existingChart;
    try {
        // Chart.js v4.x method
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // Create new chart
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Quantity',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bar
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 14
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `Quantity: ${parseFloat(context.raw).toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantity'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Material'
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
 * Update summary statistics display
 * @param {Array} data - The summary data
 * @param {string} category - The selected category
 * @param {number} totalValue - The total value across all materials
 * @param {number} totalQuantity - The total quantity across all materials
 */
function updateSummaryStats(data, category, totalValue, totalQuantity) {
    if (!data || !data.length) {
        $('#totalItems').text('0');
        $('#totalValue').text('$0.00');
        $('#totalQuantity').text('0');
        $('#categoryName').text('No items found');
        return;
    }

    // Update stats
    $('#totalItems').text(data.length);
    $('#totalValue').text(formatCurrency(totalValue));
    $('#totalQuantity').text(parseFloat(totalQuantity).toFixed(2));
    $('#categoryName').text(category);
}

/**
 * Export report data to CSV
 * @param {string} type - Export type ('detail' or 'summary')
 */
function exportReportData(type = 'detail') {
    const category = $('#categorySelect').val();

    if (!category) {
        showError('Please select a category before exporting');
        return;
    }

    // Build export URL
    let url = `/groups/warehouse/fifo_stock/export?category=${encodeURIComponent(category)}&type=${type}`;

    // Open in new tab/window
    window.open(url, '_blank');
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
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
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

/**
 * Create a pie chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - The chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 */
function createPieChart(canvasId, title, labels, data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Cannot find ${canvasId} canvas element`);
        return;
    }

    // Safely destroy existing chart if it exists
    let existingChart;
    try {
        // Chart.js v4.x method
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // Create color array for pie slices
    const colors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(100, 180, 220, 0.7)',
        'rgba(220, 120, 150, 0.7)',
        'rgba(180, 190, 100, 0.7)'
    ];

    // Create border color array
    const borderColors = colors.map(color => color.replace('0.7', '1'));

    // Create new chart
    try {
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
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
                        position: 'right',
                        labels: {
                            boxWidth: 15,
                            font: {
                                size: 11
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 14
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${formatCurrency(value)} (${percentage}%)`;
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