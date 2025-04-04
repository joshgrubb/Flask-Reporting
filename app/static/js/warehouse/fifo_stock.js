/**
 * FIFO Stock Cost Report JavaScript
 * 
 * Key improvements:
 * - Modified Category dropdown to support multiple selections
 * - Fixed sorting for % Change column (numeric sorting instead of text)
 * - Treats N/A % change values as 0 for filtering and display
 * - Significant Cost Increase filter properly filters data
 * - Summary stats update based on applied filters
 * - Chart displays all filtered materials
 */

// Default threshold value
const DEFAULT_THRESHOLD = 50;

// Document ready function
$(document).ready(function () {
    // Initialize multiselect for categories
    initializeCategoryMultiselect();

    // Load available categories
    loadCategories();

    // Event handlers
    $('#applyFilters').click(function () {
        const selectedCategories = $('#categorySelect').val() || [];
        const thresholdValue = parseInt($('#thresholdInput').val());

        if (selectedCategories.length > 0) {
            if (isNaN(thresholdValue) || thresholdValue < 0) { // Allow 0% threshold
                showError('Please enter a valid threshold value (minimum 0%)');
                return;
            }

            loadInventoryData(selectedCategories, thresholdValue);
            $('#exportDropdown').prop('disabled', false);
        } else {
            showError('Please select at least one category');
            $('#exportDropdown').prop('disabled', true);
        }
    });

    // Reset threshold to default
    $('#resetThreshold').click(function () {
        $('#thresholdInput').val(DEFAULT_THRESHOLD);

        // If data is already loaded, apply the new threshold immediately
        if (window.costTrendData) {
            applyThresholdFilter(DEFAULT_THRESHOLD);
        }
    });

    // Apply threshold filter when input changes
    $('#thresholdInput').on('input', function () {
        const newThreshold = parseInt($(this).val());
        if (!isNaN(newThreshold) && newThreshold >= 0 && window.costTrendData) { // Allow 0% threshold
            applyThresholdFilter(newThreshold);
        }
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
        } else {
            // If no material is selected, display all filtered materials
            displayAllFilteredMaterials(thresholdValue);
        }
    });
});

/**
 * Initialize the category multiselect dropdown
 */
function initializeCategoryMultiselect() {
    // Initialize select2 for multiselect if available
    if ($.fn.select2) {
        $('#categorySelect').select2({
            placeholder: 'Select categories',
            allowClear: true,
            multiple: true,
            width: '100%'
        });
    } else if ($.fn.multiselect) {
        // Fallback to bootstrap multiselect
        $('#categorySelect').multiselect({
            includeSelectAllOption: true,
            nonSelectedText: 'Select categories',
            enableFiltering: true
        });
    }
}

/**
 * Apply threshold filter to the data tables and update summary stats
 * @param {number} threshold - The threshold value to apply
 */
function applyThresholdFilter(threshold) {
    // Update the display of the threshold value
    updateThresholdAlert(threshold);

    // Store the filtered data
    let filteredData = [];

    // Redraw tables with new threshold if they exist
    if ($.fn.DataTable.isDataTable('#costTrendTable')) {
        const table = $('#costTrendTable').DataTable();

        // Get filtered data
        filteredData = getFilteredData(window.costTrendData, threshold);

        // Redraw the table
        table.draw();

        // Update summary stats with filtered data
        updateFilteredSummaryStats(filteredData);

        // Update chart to show all filtered materials
        displayAllFilteredMaterials(threshold);
    }
}

/**
 * Get data filtered by the threshold
 * @param {Array} data - The original data array
 * @param {number} threshold - The threshold to filter by
 * @returns {Array} - Filtered data array
 */
function getFilteredData(data, threshold) {
    if (!data || !Array.isArray(data)) return [];

    return data.filter(row => {
        // Get percent change (null becomes 0)
        const percentChange = row.PercentChange === null ? 0 : parseFloat(row.PercentChange);

        // Filter based on threshold - include all values >= threshold
        return percentChange >= threshold;
    });
}

/**
 * Update summary statistics based on filtered data
 * @param {Array} filteredData - The filtered data array
 */
function updateFilteredSummaryStats(filteredData) {
    if (!filteredData || !filteredData.length) {
        $('#totalItems').text('0');
        $('#totalValue').text('$0.00');
        $('#totalQuantity').text('0');
        return;
    }

    // Count unique materials
    const uniqueMaterials = new Set();
    filteredData.forEach(item => uniqueMaterials.add(item.MATERIALUID));

    // Calculate total quantity and value
    let totalQuantity = 0;
    let totalValue = 0;

    filteredData.forEach(item => {
        const quantity = parseFloat(item.QUANTITY) || 0;
        const unitCost = parseFloat(item.UNITCOST) || 0;

        totalQuantity += quantity;
        totalValue += quantity * unitCost;
    });

    // Update the stats displays
    $('#totalItems').text(uniqueMaterials.size);
    $('#totalValue').text(formatCurrency(totalValue));
    $('#totalQuantity').text(totalQuantity.toFixed(2));
}

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

    // Clear existing options
    dropdown.empty();

    // Filter out blank/null/empty categories
    const validCategories = categories.filter(cat => cat && cat.trim() !== '');

    // Add categories as options
    validCategories.forEach(category => {
        dropdown.append($('<option></option>').val(category).text(category));
    });

    // Trigger change to update any select2 or multiselect plugins
    dropdown.trigger('change');
}

/**
 * Load inventory data for the selected category(ies)
 * @param {Array|string} categories - The selected category or categories
 * @param {number} threshold - The threshold for significant cost increases
 */
function loadInventoryData(categories, threshold = DEFAULT_THRESHOLD) {
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
            categories: Array.isArray(categories) ? categories.join(',') : categories,
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
                $('#summaryStats').show();

                // Get filtered data
                const filteredData = getFilteredData(response.data, threshold);

                // Initialize cost trend table with the threshold
                initCostTrendTable(response.data, threshold);

                // Update summary stats with filtered data
                updateFilteredSummaryStats(filteredData);

                // Populate material dropdown for line charts
                populateMaterialDropdown(Object.keys(response.materialData));

                // Display chart with all filtered materials
                displayAllFilteredMaterials(threshold);

                // Update the alert message with the current threshold
                updateThresholdAlert(threshold);

                // Hide loading indicator
                $('#costTrendTableContainer').removeClass('loading');
            } else {
                showError('Error loading cost trend data: ' + response.error);
                $('#costTrendTableContainer').removeClass('loading');
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading cost trend data: ' + error);
            $('#costTrendTableContainer').removeClass('loading');
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
            The threshold filter is currently set to ${threshold}% and only showing items with price increases at or above this value.
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
                // Improved % Change column with proper numeric sorting, treating N/A as 0
                data: 'PercentChange',
                render: function (data, type, row) {
                    // For sorting, use the raw numeric value (treat null as 0)
                    if (type === 'sort') {
                        return data === null ? 0 : parseFloat(data);
                    }

                    // For display, show 0% if null
                    if (data === null || data === undefined) {
                        return '0%';
                    }

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
            }
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
            // If PercentChange exceeds threshold, highlight the row
            const percentChange = data.PercentChange === null ? 0 : data.PercentChange;
            if (percentChange > significantThreshold) {
                $(row).addClass('table-danger');
            }
        }
    };

    // Initialize DataTable
    const table = $('#costTrendTable').DataTable(dataTableOptions);

    // Add custom filtering for % change based on threshold
    $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex, rowData) {
            // Only apply to cost trend table
            if (settings.nTable.id !== 'costTrendTable') return true;

            // Get current threshold
            const threshold = parseInt($('#thresholdInput').val()) || significantThreshold;

            // Get percent change (null becomes 0)
            const percentChange = rowData.PercentChange === null ? 0 : parseFloat(rowData.PercentChange);

            // Filter based on threshold - include all values >= threshold
            return percentChange >= threshold;
        }
    );

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

    // Clear existing options
    dropdown.find('option').remove();

    // Add default "All Materials" option
    dropdown.append($('<option></option>').val('').text('All Filtered Materials'));

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
 * Display chart with all materials that meet the threshold criteria
 * @param {number} threshold - The threshold value to filter by
 */
function displayAllFilteredMaterials(threshold = DEFAULT_THRESHOLD) {
    // Get data filtered by threshold
    const filteredData = getFilteredData(window.costTrendData, threshold);

    if (!filteredData || !filteredData.length) {
        // If no data after filtering, show empty chart with message
        createEmptyChart('costTrendChart', 'No materials meet the current threshold criteria');
        return;
    }

    // Group data by material
    const materialGroups = {};

    filteredData.forEach(item => {
        const materialId = item.MATERIALUID;
        if (!materialGroups[materialId]) {
            materialGroups[materialId] = [];
        }
        materialGroups[materialId].push(item);
    });

    // Prepare dataset for chart
    const datasets = [];
    const colors = [
        'rgba(54, 162, 235, 0.7)', // blue
        'rgba(255, 99, 132, 0.7)', // red
        'rgba(75, 192, 192, 0.7)', // green
        'rgba(153, 102, 255, 0.7)', // purple
        'rgba(255, 159, 64, 0.7)', // orange
        'rgba(201, 203, 207, 0.7)', // grey
        'rgba(255, 205, 86, 0.7)', // yellow
    ];

    // Get up to 10 materials with highest percent changes
    const materialIds = Object.keys(materialGroups);
    const materialsToShow = materialIds.slice(0, 10); // Limit to 10 materials

    // Create datasets for each material
    materialsToShow.forEach((materialId, index) => {
        const items = materialGroups[materialId];
        if (!items || !items.length) return;

        // Sort by purchase date
        items.sort((a, b) => new Date(a.PURCHASEDATE) - new Date(b.PURCHASEDATE));

        // Extract data
        const data = items.map(item => parseFloat(item.UNITCOST));

        // Get material description
        const description = items[0].DESCRIPTION || materialId;

        // Get color (cycle through color array)
        const colorIndex = index % colors.length;

        // Create dataset
        datasets.push({
            label: materialId,
            data: data,
            borderColor: colors[colorIndex].replace('0.7', '1'),
            backgroundColor: colors[colorIndex],
            fill: false,
            tension: 0.1
        });
    });

    // Create chart with all datasets
    createMultiSeriesChart('costTrendChart', 'Unit Cost Trends for Filtered Materials', datasets, threshold);
}

/**
 * Create an empty chart with a message
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} message - The message to display
 */
function createEmptyChart(canvasId, message) {
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

    // Destroy existing chart if it exists
    let existingChart;
    try {
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // Create empty chart with message
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: message,
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

/**
 * Create a multi-series line chart for multiple materials
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - The chart title
 * @param {Array} datasets - Array of datasets for the chart
 * @param {number} threshold - The threshold value
 */
function createMultiSeriesChart(canvasId, title, datasets, threshold) {
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

    // Destroy existing chart if it exists
    let existingChart;
    try {
        existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
    } catch (e) {
        console.log('No existing chart found or using older Chart.js version');
    }

    // If no datasets, show empty chart
    if (!datasets || !datasets.length) {
        createEmptyChart(canvasId, 'No data available');
        return;
    }

    // Create chart
    new Chart(canvas, {
        type: 'line',
        data: {
            datasets: datasets
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
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${formatCurrency(value)}`;
                        }
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12
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
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Purchase Point'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
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

    // Calculate percent changes for data points, treating null as 0
    const percentChanges = data.map((value, index) => {
        if (index === 0) return 0;
        const prevValue = data[index - 1];
        return ((value - prevValue) / prevValue) * 100;
    });

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
                        const percentChange = percentChanges[index];

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

                                // Calculate percent change, show 0% for the first data point
                                let changeText = '';
                                if (index > 0) {
                                    const percentChange = percentChanges[index];
                                    changeText = ` (${percentChange > 0 ? '+' : ''}${percentChange.toFixed(2)}%)`;
                                } else {
                                    changeText = ' (0%)';
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
    const categories = $('#categorySelect').val();
    const threshold = parseInt($('#thresholdInput').val()) || DEFAULT_THRESHOLD;

    if (!categories || categories.length === 0) {
        showError('Please select at least one category before exporting');
        return;
    }

    // Build export URL with selected categories and threshold
    const categoryParam = Array.isArray(categories) ? categories.join(',') : categories;
    let url = `/groups/warehouse/fifo_stock/export?categories=${encodeURIComponent(categoryParam)}&type=${type}&threshold=${threshold}`;

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