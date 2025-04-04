/**
 * FIFO Stock Cost Report JavaScript
 * 
 * This file handles the interactive functionality for the FIFO Stock Cost report,
 * including loading data, initializing charts, tables, and handling user interactions.
 * Modified to show unit cost trends over time and highlight significant increases.
 */

// Default threshold value
const DEFAULT_THRESHOLD = 50;

// Document ready function
$(document).ready(function () {
    // Load available categories
    loadCategories();

    // Event handlers
    $('#applyFilters').click(function () {
        const selectedCategory = $('#categorySelect').val();
        const thresholdValue = parseInt($('#thresholdInput').val());

        if (selectedCategory) {
            if (isNaN(thresholdValue) || thresholdValue < 1) {
                showError('Please enter a valid threshold value (minimum 1%)');
                return;
            }

            loadInventoryData(selectedCategory, thresholdValue);
            $('#exportDropdown').prop('disabled', false);
        } else {
            showError('Please select a category');
            $('#exportDropdown').prop('disabled', true);
        }
    });

    // Reset threshold to default
    $('#resetThreshold').click(function () {
        $('#thresholdInput').val(DEFAULT_THRESHOLD);
    });

    // Handle the export dropdown options
    $('#exportDetail').click(function () {
        exportReportData('detail');
    });

    $('#exportSummary').click(function () {
        exportReportData('summary');
    });

    $('#exportTrends').click(function () {
        exportReportData('trends');
    });

    // Handle material selection for line chart
    $('#materialSelect').change(function () {
        const selectedMaterial = $(this).val();
        const thresholdValue = parseInt($('#thresholdInput').val()) || DEFAULT_THRESHOLD;

        if (selectedMaterial) {
            displayMaterialCostTrend(selectedMaterial, thresholdValue);
        }
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
 * @param {number} threshold - The threshold for significant cost increases
 */
function loadInventoryData(category, threshold = DEFAULT_THRESHOLD) {
    // Show loading indicators and hide results sections
    $('#costTrendTableContainer, #summaryTableContainer').addClass('loading');
    $('#initialMessage').hide();
    $('#summaryStats, #costTrendSection, #materialChartsSection, #summaryDataSection').hide();

    // Store the current threshold value
    window.currentThreshold = threshold;

    // Global variable to store cost trend data
    window.costTrendData = null;

    // Load cost trend data (unit cost over time)
    $.ajax({
        url: '/groups/warehouse/fifo_stock/cost-trends',
        data: {
            category: category,
            threshold: threshold
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Store data globally for use in charts
                window.costTrendData = response.data;
                window.materialData = response.materialData;

                // Show cost trend section
                $('#costTrendSection').show();
                $('#materialChartsSection').show();

                // Initialize cost trend table with the user-defined threshold
                initCostTrendTable(response.data, threshold);

                // Populate material dropdown for line charts
                populateMaterialDropdown(Object.keys(response.materialData));

                // Update the alert message with the current threshold
                updateThresholdAlert(threshold);
            } else {
                showError('Error loading cost trend data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading cost trend data: ' + error);
        },
        complete: function () {
            $('#costTrendTableContainer').removeClass('loading');
        }
    });

    // Load summary data
    $.ajax({
        url: '/groups/warehouse/fifo_stock/summary',
        data: {
            category: category,
            threshold: threshold
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                // Show summary sections
                $('#summaryStats, #summaryDataSection').show();

                // Initialize summary table with the user-defined threshold
                initSummaryTable(response.data, threshold);

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
 * Update the threshold alert message
 * @param {number} threshold - The current threshold value
 */
function updateThresholdAlert(threshold) {
    const alertElement = $('#costTrendSection .alert-warning');
    if (alertElement.length) {
        alertElement.html(`
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Note:</strong> Rows highlighted in red indicate a significant increase in unit cost (above ${threshold}%), 
            which might indicate a potential error where total cost was entered instead of unit cost. 
            You can adjust the threshold using the filter above.
        `);
    }
}

/**
 * Initialize the cost trend table
 * @param {Array} data - The cost trend data
 * @param {number} significantThreshold - Threshold for significant cost increases
 */
function initCostTrendTable(data, significantThreshold) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#costTrendTable')) {
        $('#costTrendTable').DataTable().destroy();
    }

    // Create options object for DataTable
    const dataTableOptions = {
        data: data,
        columns: [
            { data: 'MATERIALUID' },
            { data: 'DESCRIPTION' },
            {
                data: 'PURCHASEDATE',
                render: function (data) {
                    return formatDate(data);
                }
            },
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
                data: 'PreviousCost',
                render: function (data) {
                    return data ? formatCurrency(data) : 'N/A';
                }
            },
            {
                data: 'PercentChange',
                render: function (data) {
                    if (data === 0 || !data) return 'N/A';

                    const formattedValue = parseFloat(data).toFixed(2) + '%';

                    // Use color coding based on percentage change
                    if (data > significantThreshold) {
                        return `<span class="text-danger fw-bold">${formattedValue}</span>`;
                    } else if (data > significantThreshold * 0.4) {
                        return `<span class="text-warning">${formattedValue}</span>`;
                    } else if (data < 0) {
                        return `<span class="text-success">${formattedValue}</span>`;
                    }

                    return formattedValue;
                }
            },
        ],
        pageLength: 25,
        order: [[0, 'asc'], [2, 'asc']], // Sort by Material ID, then Purchase Date
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        // Row styling for significant increases
        createdRow: function (row, data) {
            if (data.PercentChange > significantThreshold) {
                $(row).addClass('table-danger');
            }
        }
    };

    // Initialize DataTable
    const table = $('#costTrendTable').DataTable(dataTableOptions);

    // Add a filter by Material ID
    new $.fn.dataTable.SearchPanes(table, {});
    table.searchPanes.container().prependTo('#costTrendTableContainer');
    table.searchPanes.resizePanes();

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
 * @param {number} threshold - The threshold for significant cost increases
 */
function initSummaryTable(data, threshold = DEFAULT_THRESHOLD) {
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
                data: 'MinUnitCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'MaxUnitCost',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: 'PercentIncrease',
                render: function (data) {
                    if (!data) return 'N/A';

                    const formattedValue = parseFloat(data).toFixed(2) + '%';

                    // Use color coding based on percentage change
                    if (data > threshold) {
                        return `<span class="text-danger fw-bold">${formattedValue}</span>`;
                    } else if (data > threshold * 0.4) { // Warning at 40% of threshold
                        return `<span class="text-warning">${formattedValue}</span>`;
                    }

                    return formattedValue;
                }
            },
            {
                data: 'TotalValue',
                render: function (data) {
                    return formatCurrency(data);
                }
            },
            {
                data: null,
                render: function (data) {
                    return formatDate(data.OldestPurchaseDate) + ' - ' + formatDate(data.NewestPurchaseDate);
                }
            }
        ],
        pageLength: 10,
        order: [[7, 'desc']], // Sort by Total Value, highest first
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)"
        },
        // Row styling for significant increases
        createdRow: function (row, data) {
            if (data.PercentIncrease > threshold) {
                $(row).addClass('table-danger');
            }
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
 * Populate material dropdown for line charts
 * @param {Array} materials - Array of material IDs
 */
function populateMaterialDropdown(materials) {
    const dropdown = $('#materialSelect');

    // Clear existing options except the first one
    dropdown.find('option:not(:first)').remove();

    // Sort materials for easier selection
    materials.sort();

    // Add materials as options
    materials.forEach(materialId => {
        // Find description for this material
        let description = '';
        if (window.materialData && window.materialData[materialId] && window.materialData[materialId].length > 0) {
            description = window.materialData[materialId][0].DESCRIPTION || '';
        }

        const displayText = description ? `${materialId} - ${description}` : materialId;
        dropdown.append($('<option></option>').val(materialId).text(displayText));
    });
}

/**
 * Display the cost trend chart for a specific material
 * @param {string} materialId - The material ID to display
 * @param {number} threshold - The threshold for significant cost increases
 */
function displayMaterialCostTrend(materialId, threshold = DEFAULT_THRESHOLD) {
    // Check if material data exists
    if (!window.materialData || !window.materialData[materialId]) {
        showError('Material data not found');
        return;
    }

    // Get data for this material
    const materialItems = window.materialData[materialId];

    // Sort by purchase date
    materialItems.sort((a, b) => new Date(a.PURCHASEDATE) - new Date(b.PURCHASEDATE));

    // Extract data for the chart
    const labels = materialItems.map(item => formatDate(item.PURCHASEDATE));
    const unitCosts = materialItems.map(item => parseFloat(item.UNITCOST));

    // Get material description
    const description = materialItems[0].DESCRIPTION || materialId;

    // Create or update the chart
    createLineChart('costTrendChart', `Unit Cost Trend for ${materialId} - ${description}`, labels, unitCosts, threshold);
}

/**
 * Create a line chart for cost trends
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - The chart title
 * @param {Array} labels - Array of labels (dates)
 * @param {Array} data - Array of data values (unit costs)
 * @param {number} threshold - The threshold for significant cost increases
 */
function createLineChart(canvasId, title, labels, data, threshold = DEFAULT_THRESHOLD) {
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
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Unit Cost',
                    data: data,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1, // Slight curve in the line
                    pointBackgroundColor: data.map((value, index) => {
                        if (index === 0) return 'rgba(54, 162, 235, 1)';

                        // Highlight significant increases
                        const prevValue = data[index - 1];
                        const percentChange = ((value - prevValue) / prevValue) * 100;

                        if (percentChange > threshold) return 'rgba(255, 0, 0, 1)';
                        if (percentChange > threshold * 0.4) return 'rgba(255, 165, 0, 1)';
                        return 'rgba(54, 162, 235, 1)';
                    }),
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const value = context.raw;
                                const index = context.dataIndex;
                                const unitCost = formatCurrency(value);

                                // Calculate percent change
                                let changeText = '';
                                if (index > 0) {
                                    const prevValue = data[index - 1];
                                    const percentChange = ((value - prevValue) / prevValue) * 100;
                                    changeText = ` (${percentChange > 0 ? '+' : ''}${percentChange.toFixed(2)}%)`;
                                }

                                return `Unit Cost: ${unitCost}${changeText}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Unit Cost'
                        },
                        ticks: {
                            callback: function (value) {
                                return formatCurrency(value);
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Purchase Date'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating line chart:', error);
        showError('Failed to create chart: ' + error.message);
    }
}

/**
 * Export report data to CSV
 * @param {string} type - Export type ('detail', 'summary', or 'trends')
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