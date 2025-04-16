/**
 * Fleet Costs Report JavaScript
 * 
 * This file handles the interactive functionality for the Fleet Costs report,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
$(document).ready(function () {
    // Initialize date picker
    if ($("#startDate, #endDate").length > 0 && typeof flatpickr === 'function') {
        flatpickr("#startDate, #endDate", {
            dateFormat: "Y-m-d"
        });
    }

    // Initial data load
    loadAllData();

    // Set up event listeners for the tabs to load data only when a tab is activated
    $('#dataTabs button').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).data('bs-target');

        if (targetId === '#work-orders') {
            // Reload work orders data
            loadWorkOrdersData();
        } else if (targetId === '#department-summary') {
            // Reload department summary data
            loadDepartmentSummaryData();
        } else if (targetId === '#vehicle-summary') {
            // Reload vehicle summary data
            loadVehicleSummaryData();
        } else if (targetId === '#time-series') {
            // Reload time series data
            loadTimeSeriesData();
        }
    });

    // Event handlers
    $('#applyFilters').click(function () {
        loadAllData();
    });

    $('#resetFilters').click(function () {
        // Reset to default dates (last 90 days)
        const today = new Date();
        const endDate = today.toISOString().slice(0, 10);

        const startDate = new Date();
        startDate.setDate(today.getDate() - 90);
        const formattedStartDate = startDate.toISOString().slice(0, 10);

        $('#startDate').val(formattedStartDate);
        $('#endDate').val(endDate);

        // Reset department filter
        $('#department').val('');

        // Event handler for time interval change
        $('#updateTimeSeries').click(function () {
            loadTimeSeriesData();
        });

        // Reload data with reset filters
        loadAllData();
    });

    $('#exportData').click(function () {
        exportReportData();
    });
});

/**
 * Load all data for all tabs
 */
function loadAllData() {
    loadWorkOrdersData();
    loadDepartmentSummaryData();
    loadVehicleSummaryData();

    // Only load time series if that tab is active
    if ($('#time-series-tab').hasClass('active')) {
        loadTimeSeriesData();
    }
}

/**
 * Load work orders data
 */
function loadWorkOrdersData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const department = $('#department').val();

    // Show loading indicator
    $('#workOrdersTableContainer').addClass('loading');

    // Update filter info text
    updateFilterInfo(department);

    // Load data from API
    $.ajax({
        url: '/groups/public_works/fleet_costs/data',
        data: {
            start_date: startDate,
            end_date: endDate,
            department: department
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initWorkOrdersTable(response.data);
                updateWorkOrderCount(response.data.length);
                updateTotalCosts(response.data);
            } else {
                showError('Error loading work orders data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading work orders data: ' + error);
        },
        complete: function () {
            $('#workOrdersTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the work orders data table
 * @param {Array} data - The work orders data
 */
function initWorkOrdersTable(data) {
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

    // Format data for display
    const formattedData = data.map(item => {
        // Calculate total cost
        const laborCost = item.WOLABORCOST || 0;
        const materialCost = item.WOMATCOST || 0;
        const totalCost = laborCost + materialCost;

        return {
            ...item,
            ACTUALFINISHDATE: formatDate(item.ACTUALFINISHDATE),
            WOLABORCOST: formatCurrency(laborCost),
            WOMATCOST: formatCurrency(materialCost),
            TotalCost: formatCurrency(totalCost), // Add calculated total cost
            Department: item.Department || 'N/A',
            Model: item.Model || 'N/A'
        };
    });

    // Initialize DataTable
    const table = $('#workOrdersTable').DataTable({
        data: formattedData,
        columns: [
            { data: 'WORKORDERID' },
            { data: 'ENTITYUID', title: 'Vehicle ID' },
            { data: 'Model', title: 'Vehicle Model' },
            { data: 'Department' },
            { data: 'ACTUALFINISHDATE', title: 'Finish Date' },
            { data: 'WOLABORCOST', title: 'Labor Cost' },
            { data: 'WOMATCOST', title: 'Material Cost' },
            { data: 'TotalCost', title: 'Total Cost' },
            { data: 'STATUS' }
        ],
        pageLength: 25,
        order: [[4, 'desc']], // Sort by finish date, newest first
        language: {
            search: "Search:",
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
 * Load department summary data
 */
function loadDepartmentSummaryData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();

    // Show loading indicator
    $('#departmentChartContainer').addClass('loading');

    // Load data from API
    $.ajax({
        url: '/groups/public_works/fleet_costs/summary/department',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initDepartmentSummaryChart(response.data);
                initDepartmentSummaryTable(response.data);
            } else {
                showError('Error loading department summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading department summary data: ' + error);
        },
        complete: function () {
            $('#departmentChartContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the department summary chart
 * @param {Array} data - The department summary data
 */
function initDepartmentSummaryChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('departmentCostChart');
    if (!canvas) {
        console.error('Cannot find departmentCostChart canvas element');
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

    // Sort data by total cost (descending)
    data.sort((a, b) => (b.TotalCost || 0) - (a.TotalCost || 0));

    // Limit to top 10 departments
    const topData = data.slice(0, 10);

    // Prepare data for chart
    const labels = topData.map(item => item.Department || 'Unknown');
    const laborValues = topData.map(item => item.TotalLaborCost || 0);
    const materialValues = topData.map(item => item.TotalMaterialCost || 0);

    // Create stacked bar chart
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Labor Cost',
                        data: laborValues,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Material Cost',
                        data: materialValues,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
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
                    },
                    title: {
                        display: true,
                        text: 'Top 10 Departments by Cost'
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Department'
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Cost ($)'
                        },
                        ticks: {
                            callback: function (value) {
                                return formatCurrency(value, false);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating department chart:', error);
        showError('Failed to create department chart: ' + error.message);
    }
}

/**
 * Initialize the department summary table
 * @param {Array} data - The department summary data
 */
function initDepartmentSummaryTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#departmentSummaryTable')) {
        $('#departmentSummaryTable').DataTable().destroy();
    }

    // Format data for display
    const formattedData = data.map(item => {
        return {
            Department: item.Department || 'Unknown',
            WorkOrderCount: item.WorkOrderCount || 0,
            LaborCost: formatCurrency(item.TotalLaborCost || 0),
            MaterialCost: formatCurrency(item.TotalMaterialCost || 0),
            TotalCost: formatCurrency(item.TotalCost || 0)
        };
    });

    // Initialize DataTable
    const table = $('#departmentSummaryTable').DataTable({
        data: formattedData,
        columns: [
            { data: 'Department' },
            { data: 'WorkOrderCount', title: 'Work Orders' },
            { data: 'LaborCost', title: 'Labor Cost' },
            { data: 'MaterialCost', title: 'Material Cost' },
            { data: 'TotalCost', title: 'Total Cost' }
        ],
        pageLength: 10,
        order: [[4, 'desc']], // Sort by total cost, highest first
        language: {
            search: "Search departments:"
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
 * Load vehicle summary data
 */
function loadVehicleSummaryData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const department = $('#department').val();

    // Show loading indicator
    $('#vehicleSummaryTableContainer').addClass('loading');

    // Load data from API
    $.ajax({
        url: '/groups/public_works/fleet_costs/summary/vehicle',
        data: {
            start_date: startDate,
            end_date: endDate,
            department: department
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                initVehicleSummaryTable(response.data);
                initTopVehiclesChart(response.data);
            } else {
                showError('Error loading vehicle summary data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading vehicle summary data: ' + error);
        },
        complete: function () {
            $('#vehicleSummaryTableContainer').removeClass('loading');
        }
    });
}

/**
 * Initialize the vehicle summary table
 * @param {Array} data - The vehicle summary data
 */
function initVehicleSummaryTable(data) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#vehicleSummaryTable')) {
        $('#vehicleSummaryTable').DataTable().destroy();
    }

    // Format data for display
    const formattedData = data.map(item => {
        return {
            VehicleID: item.VehicleID || 'Unknown',
            VehicleModel: item.VehicleModel || 'Unknown',
            Department: item.Department || 'Unknown',
            WorkOrderCount: item.WorkOrderCount || 0,
            LaborCost: formatCurrency(item.TotalLaborCost || 0),
            MaterialCost: formatCurrency(item.TotalMaterialCost || 0),
            TotalCost: formatCurrency(item.TotalCost || 0)
        };
    });

    // Initialize DataTable
    const table = $('#vehicleSummaryTable').DataTable({
        data: formattedData,
        columns: [
            { data: 'VehicleID' },
            { data: 'VehicleModel' },
            { data: 'Department' },
            { data: 'WorkOrderCount', title: 'Work Orders' },
            { data: 'LaborCost', title: 'Labor Cost' },
            { data: 'MaterialCost', title: 'Material Cost' },
            { data: 'TotalCost', title: 'Total Cost' }
        ],
        pageLength: 10,
        order: [[6, 'desc']], // Sort by total cost, highest first
        language: {
            search: "Search vehicles:"
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
 * Initialize the top vehicles chart
 * @param {Array} data - The vehicle summary data
 */
function initTopVehiclesChart(data) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('topVehiclesChart');
    if (!canvas) {
        console.error('Cannot find topVehiclesChart canvas element');
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

    // Sort data by total cost (descending)
    data.sort((a, b) => (b.TotalCost || 0) - (a.TotalCost || 0));

    // Limit to top 10 vehicles
    const topData = data.slice(0, 10);

    // Prepare data for chart
    const labels = topData.map(item => `${item.VehicleID} (${item.VehicleModel || 'Unknown'})`);
    const laborValues = topData.map(item => item.TotalLaborCost || 0);
    const materialValues = topData.map(item => item.TotalMaterialCost || 0);

    // Create stacked bar chart
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Labor Cost',
                        data: laborValues,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Material Cost',
                        data: materialValues,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
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
                    },
                    title: {
                        display: true,
                        text: 'Top 10 Vehicles by Cost'
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Vehicle'
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Cost ($)'
                        },
                        ticks: {
                            callback: function (value) {
                                return formatCurrency(value, false);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating vehicle chart:', error);
        showError('Failed to create vehicle chart: ' + error.message);
    }
}
/**
 * Load time series data with improved handling
 */
function loadTimeSeriesData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const department = $('#department').val();
    const interval = $('#timeInterval').val();

    // Show loading indicator
    $('#timeSeriesChartContainer').addClass('loading');

    console.log(`Loading time series data with interval: ${interval}, date range: ${startDate} to ${endDate}`);

    // Load data from API
    $.ajax({
        url: '/groups/public_works/fleet_costs/time-series',
        data: {
            start_date: startDate,
            end_date: endDate,
            department: department,
            interval: interval
        },
        dataType: 'json',
        success: function (response) {
            if (response.success) {
                console.log('Time series data received, count:', response.data.length);

                if (response.data.length === 0) {
                    // Handle empty data case
                    showError('No data available for the selected time period');
                    $('#timeSeriesChartContainer').removeClass('loading');
                    return;
                }

                // Enhanced debugging
                logTimeSeriesData(response.data, interval);

                initTimeSeriesChart(response.data, interval);
                initTimeSeriesTable(response.data, interval);
            } else {
                showError('Error loading time series data: ' + response.error);
            }
        },
        error: function (xhr, status, error) {
            showError('Error loading time series data: ' + error);
            console.error('AJAX error details:', xhr.responseText);
        },
        complete: function () {
            $('#timeSeriesChartContainer').removeClass('loading');
        }
    });
}

/**
 * Helper function to log and debug time series data with fixed date parsing
 * @param {Array} data - The time series data
 * @param {string} interval - The time interval
 */
function logTimeSeriesData(data, interval) {
    // Check for specific months or years
    const currentYear = new Date().getFullYear();

    if (interval === 'month') {
        // Map to track which months we've found
        const foundMonths = {};

        // Process each data item
        data.forEach(item => {
            let periodDate = null;

            // Handle various date formats
            if (typeof item.TimePeriod === 'string') {
                // Try parsing date - handle both ISO format and SQL Server format
                const isoMatch = item.TimePeriod.match(/^(\d{4})-(\d{2})-(\d{2})/);
                if (isoMatch) {
                    const year = parseInt(isoMatch[1], 10);
                    const month = parseInt(isoMatch[2], 10) - 1; // JS months are 0-indexed

                    // Create a month key for tracking
                    const monthKey = `${year}-${month + 1}`;

                    // Check if we haven't logged this month yet
                    if (!foundMonths[monthKey]) {
                        foundMonths[monthKey] = true;
                        const monthDate = new Date(year, month, 1);
                        console.log(`Found data for ${monthDate.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })}`);
                    }
                }
            }
        });

        // Check for current month specifically
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentMonthKey = `${currentYear}-${currentMonth + 1}`;
        if (foundMonths[currentMonthKey]) {
            console.log(`Current month (${now.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })}) data found!`);
        }
    } else if (interval === 'year') {
        // Handle year interval similarly
        const foundYears = {};

        data.forEach(item => {
            if (typeof item.TimePeriod === 'string') {
                const yearMatch = item.TimePeriod.match(/^(\d{4})/);
                if (yearMatch) {
                    const year = parseInt(yearMatch[1], 10);

                    if (!foundYears[year]) {
                        foundYears[year] = true;
                        console.log(`Found data for year ${year}`);
                    }
                }
            }
        });
    }

    // Log the raw received data for detailed debugging
    console.log('Raw time series data:', JSON.stringify(data.map(item => ({
        period: item.TimePeriod,
        workOrders: item.WorkOrderCount,
        laborCost: item.TotalLaborCost,
        materialCost: item.TotalMaterialCost,
        totalCost: item.TotalCost
    }))));
}

/**
 * Parse a date string with timezone-aware handling
 * @param {string|Date} dateValue - The date to parse
 * @returns {Date|null} - Parsed Date object or null if invalid
 */
function parseTimePeriod(dateValue) {
    if (!dateValue) {
        return null;
    }

    // If already a Date object
    if (dateValue instanceof Date) {
        return isNaN(dateValue.getTime()) ? null : dateValue;
    }

    // For string values
    if (typeof dateValue === 'string') {
        try {
            // Handle YYYY-MM-DD format (most common from SQL Server)
            const isoMatch = dateValue.match(/^(\d{4})-(\d{2})-(\d{2})/);
            if (isoMatch) {
                const year = parseInt(isoMatch[1], 10);
                const month = parseInt(isoMatch[2], 10) - 1; // JS months are 0-indexed
                const day = parseInt(isoMatch[3], 10);

                // Create date in local timezone (not UTC) to avoid timezone shifts
                // This is critical - prevents the browser from interpreting dates in UTC
                // which can cause them to shift to the previous day/month
                return new Date(year, month, day);
            }

            // Try direct Date constructor as fallback
            // NOTE: This can be problematic with timezone shifting
            const directDate = new Date(dateValue);
            if (!isNaN(directDate.getTime())) {
                // Ensure we're using the date as specified (not shifted by timezone)
                const year = directDate.getFullYear();
                const month = directDate.getMonth();
                const day = directDate.getDate();
                return new Date(year, month, day);
            }
        } catch (error) {
            console.error("Date parsing error:", error);
        }
    }

    // If all parsing attempts fail
    return null;
}
/**
 * Initialize the time series chart with timezone-aware date handling
 * @param {Array} data - The time series data
 * @param {string} interval - The time interval (day, week, month, quarter, year)
 */
function initTimeSeriesChart(data, interval) {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly');
        showError('Chart.js library failed to load. Please check console for details.');
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('timeSeriesChart');
    if (!canvas) {
        console.error('Cannot find timeSeriesChart canvas element');
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

    // Parse and format data with improved timezone-aware date handling
    const parsedData = [];

    // Debugging raw date formats
    console.log("Raw date formats sample:", data.slice(0, 2).map(item => item.TimePeriod));

    for (let i = 0; i < data.length; i++) {
        const item = data[i];

        try {
            // Log the raw period data for inspection
            if (i < 5) {
                console.log(`Raw time period [${i}]:`, item.TimePeriod);
            }

            // Extract date components directly to avoid timezone issues
            // YYYY-MM-DD format parsing
            let periodDate = null;
            if (typeof item.TimePeriod === 'string') {
                const match = item.TimePeriod.match(/^(\d{4})-(\d{2})-(\d{2})/);
                if (match) {
                    const year = parseInt(match[1], 10);
                    const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
                    const day = parseInt(match[3], 10);
                    periodDate = new Date(year, month, day);

                    // Log constructed date to check for timezone shifting
                    if (i < 5) {
                        console.log(`Constructed date [${i}]:`,
                            periodDate.toLocaleDateString(),
                            `(${year}-${month + 1}-${day})`);
                    }
                }
            } else if (item.TimePeriod instanceof Date) {
                // Direct date object - use year, month, day to rebuild and avoid timezone issues
                const year = item.TimePeriod.getFullYear();
                const month = item.TimePeriod.getMonth();
                const day = item.TimePeriod.getDate();
                periodDate = new Date(year, month, day);
            }

            // Only add valid dates to the dataset
            if (periodDate && !isNaN(periodDate.getTime())) {
                parsedData.push({
                    periodDate: periodDate,
                    periodText: formatTimePeriod(periodDate, interval),
                    rawPeriod: item.TimePeriod,
                    laborCost: Number(item.TotalLaborCost || 0),
                    materialCost: Number(item.TotalMaterialCost || 0),
                    totalCost: Number(item.TotalCost || 0),
                    workOrders: Number(item.WorkOrderCount || 0)
                });
            } else {
                console.warn(`Skipping item with invalid date: ${item.TimePeriod}`);
            }
        } catch (error) {
            console.error('Error parsing time period:', error, item);
        }
    }

    // Sort data chronologically
    parsedData.sort((a, b) => a.periodDate.getTime() - b.periodDate.getTime());

    // Log parsed data details
    const months = parsedData.map(item =>
        item.periodDate.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })
    );
    console.log(`Parsed ${parsedData.length} valid data points out of ${data.length} total`);
    console.log('Parsed time periods:', months);

    // If no valid data, show message and exit
    if (parsedData.length === 0) {
        showError('No valid time series data available for the selected period');
        return;
    }

    // Extract data series
    const labels = parsedData.map(item => item.periodText);
    const laborCosts = parsedData.map(item => item.laborCost);
    const materialCosts = parsedData.map(item => item.materialCost);
    const totalCosts = parsedData.map(item => item.totalCost);
    const workOrders = parsedData.map(item => item.workOrders);

    // Create chart
    try {
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Cost',
                        data: totalCosts,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 3,
                        yAxisID: 'y-cost',
                        order: 1,
                        type: 'line',
                        tension: 0.1
                    },
                    {
                        label: 'Labor Cost',
                        data: laborCosts,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-cost',
                        order: 2,
                        type: 'line',
                        tension: 0.1
                    },
                    {
                        label: 'Material Cost',
                        data: materialCosts,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-cost',
                        order: 3,
                        type: 'line',
                        tension: 0.1
                    },
                    {
                        label: 'Work Orders',
                        data: workOrders,
                        backgroundColor: 'rgba(153, 102, 255, 0.5)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1,
                        yAxisID: 'y-count',
                        order: 4,
                        type: 'bar'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Fleet Costs Over Time (${getIntervalName(interval)})`
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.dataset.label || '';
                                const value = context.raw;

                                if (label === 'Work Orders') {
                                    return `${label}: ${value}`;
                                } else {
                                    return `${label}: ${formatCurrency(value)}`;
                                }
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: `Time (${getIntervalName(interval)})`
                        }
                    },
                    'y-cost': {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Cost ($)'
                        },
                        ticks: {
                            callback: function (value) {
                                return formatCurrency(value, false);
                            }
                        },
                        beginAtZero: true
                    },
                    'y-count': {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Work Order Count'
                        },
                        ticks: {
                            precision: 0
                        },
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
        console.log('Chart successfully created');
    } catch (error) {
        console.error('Error creating time series chart:', error);
        showError('Failed to create time series chart: ' + error.message);
    }
}
/**
 * Initialize the time series table with timezone-aware date handling
 * @param {Array} data - The time series data
 * @param {string} interval - The time interval
 */
function initTimeSeriesTable(data, interval) {
    // Check if DataTables is available
    if (typeof $.fn.DataTable !== 'function') {
        console.error('DataTables is not loaded properly');
        showError('DataTables library failed to load. Please check console for details.');
        return;
    }

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable('#timeSeriesTable')) {
        $('#timeSeriesTable').DataTable().destroy();
    }

    // Parse and format data with robust date handling
    const tableData = [];

    for (let i = 0; i < data.length; i++) {
        const item = data[i];

        try {
            // Extract date components directly to avoid timezone issues
            let periodDate = null;
            if (typeof item.TimePeriod === 'string') {
                const match = item.TimePeriod.match(/^(\d{4})-(\d{2})-(\d{2})/);
                if (match) {
                    const year = parseInt(match[1], 10);
                    const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
                    const day = parseInt(match[3], 10);
                    periodDate = new Date(year, month, day);
                }
            } else if (item.TimePeriod instanceof Date) {
                // Direct date object - use year, month, day to rebuild
                const year = item.TimePeriod.getFullYear();
                const month = item.TimePeriod.getMonth();
                const day = item.TimePeriod.getDate();
                periodDate = new Date(year, month, day);
            }

            // Add to table data
            if (periodDate && !isNaN(periodDate.getTime())) {
                tableData.push({
                    TimePeriod: formatTimePeriod(periodDate, interval),
                    WorkOrderCount: item.WorkOrderCount || 0,
                    LaborCost: formatCurrency(item.TotalLaborCost || 0),
                    MaterialCost: formatCurrency(item.TotalMaterialCost || 0),
                    TotalCost: formatCurrency(item.TotalCost || 0),
                    RawDate: periodDate.getTime() // For sorting
                });
            } else {
                // Add item with raw text as fallback
                tableData.push({
                    TimePeriod: String(item.TimePeriod || 'Unknown'),
                    WorkOrderCount: item.WorkOrderCount || 0,
                    LaborCost: formatCurrency(item.TotalLaborCost || 0),
                    MaterialCost: formatCurrency(item.TotalMaterialCost || 0),
                    TotalCost: formatCurrency(item.TotalCost || 0),
                    RawDate: 0 // For sorting, put unknown dates first
                });
            }
        } catch (error) {
            console.error('Error parsing time period for table:', error, item);
        }
    }

    // Sort by date
    tableData.sort((a, b) => a.RawDate - b.RawDate);

    // Debug: Log table data
    console.log('Formatted time series table data:', tableData);

    // Initialize DataTable
    const table = $('#timeSeriesTable').DataTable({
        data: tableData,
        columns: [
            { data: 'TimePeriod' },
            { data: 'WorkOrderCount' },
            { data: 'LaborCost' },
            { data: 'MaterialCost' },
            { data: 'TotalCost' }
        ],
        pageLength: 10,
        order: [[0, 'asc']], // Sort by time period, ascending
        language: {
            search: "Search:"
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
 * Format a time period based on interval
 * @param {Date} date - The date to format
 * @param {string} interval - The time interval
 * @returns {string} - Formatted time period string
 */
function formatTimePeriod(date, interval) {
    if (!date || isNaN(date.getTime())) {
        return 'Unknown';
    }

    try {
        switch (interval) {
            case 'day':
                return date.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            case 'week':
                return `Week of ${date.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                })}`;
            case 'month':
                return date.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'long'
                });
            case 'quarter': {
                const quarter = Math.floor((date.getMonth() / 3) + 1);
                return `Q${quarter} ${date.getFullYear()}`;
            }
            case 'year':
                return date.getFullYear().toString();
            default:
                return date.toLocaleDateString();
        }
    } catch (error) {
        console.error('Error formatting time period:', error);
        return String(date);
    }
}

/**
 * Get a human-readable name for the time interval
 * @param {string} interval - The time interval
 * @returns {string} - Human-readable interval name
 */
function getIntervalName(interval) {
    switch (interval) {
        case 'day': return 'Daily';
        case 'week': return 'Weekly';
        case 'month': return 'Monthly';
        case 'quarter': return 'Quarterly';
        case 'year': return 'Yearly';
        default: return 'Monthly';
    }
}
/**
 * Update work order count and date range info with timezone-safe date handling
 * @param {number} count - The number of work orders
 */
function updateWorkOrderCount(count) {
    $('#totalWorkOrders').text(count);

    // Update date range info with timezone-safe date formatting
    const startDateStr = $('#startDate').val();
    const endDateStr = $('#endDate').val();

    // Format dates safely without timezone shifting
    const formattedStartDate = formatDateSafe(startDateStr);
    const formattedEndDate = formatDateSafe(endDateStr);

    $('#dateRangeInfo').text(`From ${formattedStartDate} to ${formattedEndDate}`);
}

/**
 * Format a date string safely without timezone shifting
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDateSafe(dateString) {
    if (!dateString) return '';

    try {
        // Extract date components directly from YYYY-MM-DD format
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);

            // Create date without timezone shifting
            const date = new Date(year, month, day);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                return dateString; // Return original if parsing failed
            }

            // Format using locale-specific date format
            return date.toLocaleDateString();
        }

        // Fallback to original format function if not in expected format
        return formatDate(dateString);
    } catch (error) {
        console.error('Error safely formatting date:', error);
        return dateString;
    }
}

/**
 * Update total costs display
 * @param {Array} data - The work orders data
 */
function updateTotalCosts(data) {
    // Calculate total labor and material costs
    let totalLabor = 0;
    let totalMaterial = 0;

    data.forEach(item => {
        totalLabor += parseFloat(item.WOLABORCOST || 0);
        totalMaterial += parseFloat(item.WOMATCOST || 0);
    });

    // Update total cost displays
    $('#totalLaborCost').text(formatCurrency(totalLabor));
    $('#totalMaterialCost').text(formatCurrency(totalMaterial));
    $('#totalCost').text(formatCurrency(totalLabor + totalMaterial));
}

/**
 * Update department filter info text
 * @param {string} department - The department filter value
 */
function updateFilterInfo(department) {
    if (department) {
        $('#departmentInfo').text(`Department: ${department}`);
    } else {
        $('#departmentInfo').text('All departments');
    }
}

/**
 * Export report data to CSV
 */
function exportReportData() {
    // Get filter values
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    const department = $('#department').val();

    // Build export URL
    let url = '/groups/public_works/fleet_costs/export';
    let params = [];

    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (department) params.push(`department=${department}`);

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

        return date.toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
    }
}

/**
 * Format a number as currency
 * @param {number} amount - The amount to format
 * @param {boolean} symbol - Whether to include the currency symbol
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount, symbol = true) {
    if (amount === null || amount === undefined) return '';

    try {
        // Convert to number if it's a string
        const value = typeof amount === 'string' ? parseFloat(amount) : amount;

        // Check if value is valid number
        if (isNaN(value)) {
            return amount;
        }

        // Format as currency
        return symbol
            ? '$' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
            : value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    } catch (error) {
        console.error('Error formatting currency:', error);
        return amount;
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