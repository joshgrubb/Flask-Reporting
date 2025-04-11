/**
 * Enhanced Budget Dashboard JavaScript
 * 
 * This file handles the interactive functionality for the Budget Dashboard,
 * including loading data, initializing multiple charts, and handling user interactions.
 */

// Store chart instances globally for easy access
const chartInstances = {
    overview: null,
    department: null,
    monthly: null,
    comparison: null
};

// Document ready function
document.addEventListener('DOMContentLoaded', function () {
    // Initialize event handlers
    document.getElementById('applyFilters').addEventListener('click', loadAllData);

    document.getElementById('overviewRetryButton').addEventListener('click', function () {
        document.getElementById('overviewChartError').style.display = 'none';
        loadOverviewChart();
    });

    // Handle tab changes to load data lazily
    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (e) {
            const targetId = e.target.getAttribute('href').substring(1);

            switch (targetId) {
                case 'overview':
                    if (!chartInstances.overview) loadOverviewChart();
                    break;
                case 'departments':
                    if (!chartInstances.department) loadDepartmentChart();
                    break;
                case 'monthly':
                    if (!chartInstances.monthly) loadMonthlyChart();
                    break;
                case 'comparison':
                    if (!chartInstances.comparison) loadComparisonChart();
                    break;
            }
        });
    });

    // Export functionality
    document.getElementById('exportData').addEventListener('click', exportBudgetData);

    // Initial data load
    loadAllData();

    // Apply initial theme
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    updateDashboardTheme(isDarkMode);

    // Add theme change listener
    document.addEventListener('darkModeChanged', function () {
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        updateDashboardTheme(isDarkMode);
        updateAllChartThemes(isDarkMode);
    });
});

/**
 * Load all dashboard data
 */
function loadAllData() {
    // Reset all charts
    resetAllCharts();

    // Load KPI summary data
    loadKPISummary();

    // Load overview chart (initially visible tab)
    loadOverviewChart();

    // Load budget summary table
    loadBudgetSummary();
}

/**
 * Reset all chart instances
 */
function resetAllCharts() {
    // Destroy chart instances
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            chartInstances[key].destroy();
            chartInstances[key] = null;
        }
    });
}

/**
 * Load KPI summary cards data
 */
function loadKPISummary() {
    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query string
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    if (department) queryParams.push('department=' + encodeURIComponent(department));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL for budget summary API
    const url = '/groups/finance/budget/api/budget-summary?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateKPICards(data.data);
            } else {
                throw new Error(data.error || 'No budget data available');
            }
        })
        .catch(error => {
            console.error('Error loading budget summary:', error);

            // Show error message
            document.getElementById('budgetSummaryLoading').style.display = 'none';

            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-warning';
            errorMsg.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;

            const container = document.getElementById('budgetSummaryContainer');
            container.innerHTML = '';
            container.appendChild(errorMsg);
            container.style.display = 'block';
        });
}

/**
 * Populate budget summary table
 * @param {Array} data - Budget summary data
 */
function populateBudgetSummaryTable(data) {
    if (!data || !data.length) return;

    // Get table body element
    const tableBody = document.querySelector('#budgetSummaryTable tbody');
    if (!tableBody) {
        console.error('Table body element not found');
        return;
    }

    // Clear existing rows
    tableBody.innerHTML = '';

    // Add data rows
    data.forEach(item => {
        // Create row element
        const row = document.createElement('tr');

        // Add warning class if percent spent is high
        if (item.percent_spent > 90) {
            row.classList.add('table-danger');
        } else if (item.percent_spent > 75) {
            row.classList.add('table-warning');
        }

        // Add cells
        row.innerHTML = `
            <td>${item.fund || 'N/A'}</td>
            <td>${item.department || 'N/A'}</td>
            <td>${item.division || 'N/A'}</td>
            <td>${formatCurrency(item.total_budget)}</td>
            <td>${formatCurrency(item.total_actual)}</td>
            <td>${formatCurrency(item.total_encumbrance)}</td>
            <td>${formatCurrency(item.remaining_budget)}</td>
            <td>${item.percent_spent.toFixed(1)}%</td>
        `;

        // Add row to table
        tableBody.appendChild(row);
    });

    // Initialize DataTable if available
    if ($.fn && $.fn.DataTable) {
        // Destroy existing DataTable instance if any
        if ($.fn.DataTable.isDataTable('#budgetSummaryTable')) {
            $('#budgetSummaryTable').DataTable().destroy();
        }

        // Initialize DataTable
        $('#budgetSummaryTable').DataTable({
            pageLength: 10,
            order: [[3, 'desc']], // Sort by budget amount by default
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'csv',
                    text: '<i class="fas fa-file-csv"></i> CSV',
                    className: 'btn btn-sm btn-outline-primary'
                },
                {
                    extend: 'excel',
                    text: '<i class="fas fa-file-excel"></i> Excel',
                    className: 'btn btn-sm btn-outline-success'
                },
                {
                    extend: 'pdf',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    className: 'btn btn-sm btn-outline-danger'
                },
                {
                    extend: 'print',
                    text: '<i class="fas fa-print"></i> Print',
                    className: 'btn btn-sm btn-outline-secondary'
                }
            ]
        });
    }
}

/**
 * Export budget data to CSV
 */
function exportBudgetData() {
    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build export URL
    let url = '/groups/finance/budget/export';
    let params = [];

    if (fiscalYear) {
        params.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    }

    if (department) {
        params.push('department=' + encodeURIComponent(department));
    }

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    // Open in new tab
    window.open(url, '_blank');
}

/**
 * Update all chart themes based on dark/light mode
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updateAllChartThemes(isDarkMode) {
    // Update each chart if it exists
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            updateChartTheme(chartInstances[key], isDarkMode);
        }
    });
}

/**
 * Update a specific chart's theme
 * @param {Chart} chart - The Chart.js instance to update
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updateChartTheme(chart, isDarkMode) {
    if (!chart || !chart.options) return;

    // Define colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Update title color if exists
    if (chart.options.plugins && chart.options.plugins.title) {
        chart.options.plugins.title.color = textColor;
    }

    // Update legend colors if exists
    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
        chart.options.plugins.legend.labels.color = textColor;
    }

    // Update scales if exists
    if (chart.options.scales) {
        // X axis
        if (chart.options.scales.x) {
            if (chart.options.scales.x.ticks) {
                chart.options.scales.x.ticks.color = textColor;
            }

            if (chart.options.scales.x.grid) {
                chart.options.scales.x.grid.color = gridColor;
            }

            if (chart.options.scales.x.title) {
                chart.options.scales.x.title.color = textColor;
            }
        }

        // Y axis
        if (chart.options.scales.y) {
            if (chart.options.scales.y.ticks) {
                chart.options.scales.y.ticks.color = textColor;
            }

            if (chart.options.scales.y.grid) {
                chart.options.scales.y.grid.color = gridColor;
            }

            if (chart.options.scales.y.title) {
                chart.options.scales.y.title.color = textColor;
            }
        }

        // Y1 axis (if exists)
        if (chart.options.scales.y1) {
            if (chart.options.scales.y1.ticks) {
                chart.options.scales.y1.ticks.color = textColor;
            }

            if (chart.options.scales.y1.grid) {
                chart.options.scales.y1.grid.color = gridColor;
            }

            if (chart.options.scales.y1.title) {
                chart.options.scales.y1.title.color = textColor;
            }
        }
    }

    // Update the chart
    chart.update();
}

/**
 * Update dashboard elements styling for the current theme
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updateDashboardTheme(isDarkMode) {
    // Update table styling
    const table = document.getElementById('budgetSummaryTable');
    if (table) {
        if (isDarkMode) {
            table.classList.add('table-dark');
        } else {
            table.classList.remove('table-dark');
        }
    }

    // Update cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        if (isDarkMode) {
            card.classList.add('bg-dark');
            card.classList.add('text-light');
            card.classList.add('border-secondary');
        } else {
            card.classList.remove('bg-dark');
            card.classList.remove('text-light');
            card.classList.remove('border-secondary');
        }
    });

    // Update nav tabs
    const navTabs = document.querySelectorAll('.nav-tabs .nav-link');
    navTabs.forEach(tab => {
        if (isDarkMode) {
            tab.classList.add('text-light');
        } else {
            tab.classList.remove('text-light');
        }
    });

    // Fix card headers
    const cardHeaders = document.querySelectorAll('.card-header.bg-primary');
    cardHeaders.forEach(header => {
        if (isDarkMode) {
            header.style.backgroundColor = 'var(--primary-color) !important';
        } else {
            header.style.backgroundColor = '';
        }
    });
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
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(numValue);
    } catch (error) {
        console.error('Error formatting currency:', error);
        return '$0.00';
    }
}

/**
 * Calculate moving average for a data series
 * @param {Array} data - Array of values
 * @param {Number} period - Period for moving average
 * @returns {Array} - Moving average values
 */
function calculateMovingAverage(data, period) {
    const result = [];

    // Return empty array if no data or invalid period
    if (!data || !data.length || period <= 0 || period > data.length) {
        return result;
    }

    // Calculate moving average
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            // Not enough data points yet, push null
            result.push(null);
        } else {
            // Calculate average of last 'period' values
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j];
            }
            result.push(sum / period);
        }
    }

    return result;
}
throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch (error => {
    console.error('Error loading KPI data:', error);

    // Set default values in case of error
    document.getElementById('totalBudget').textContent = '$0';
    document.getElementById('budgetSpent').textContent = '$0';
    document.getElementById('remainingBudget').textContent = '$0';
    document.getElementById('spendingTrend').textContent = 'N/A';
});
}

/**
 * Update KPI cards with summary data
 * @param {Array} data - Budget summary data
 */
function updateKPICards(data) {
    if (!data || !data.length) return;

    // Calculate totals
    let totalBudget = 0;
    let totalActual = 0;
    let totalEncumbrance = 0;
    let remainingBudget = 0;

    data.forEach(item => {
        totalBudget += item.total_budget;
        totalActual += item.total_actual;
        totalEncumbrance += item.total_encumbrance;
    });

    remainingBudget = totalBudget - totalActual - totalEncumbrance;
    const percentSpent = totalBudget > 0 ? (totalActual / totalBudget) * 100 : 0;

    // Format and display totals
    document.getElementById('totalBudget').textContent = formatCurrency(totalBudget);
    document.getElementById('budgetSpent').textContent = formatCurrency(totalActual);
    document.getElementById('remainingBudget').textContent = formatCurrency(remainingBudget);

    // Calculate and display spending percent
    const percentElem = document.getElementById('budgetSpentPercent');
    percentElem.textContent = percentSpent.toFixed(1) + '%';

    // Add appropriate class based on spending
    percentElem.className = '';
    if (percentSpent > 90) {
        percentElem.classList.add('kpi-negative');
    } else if (percentSpent > 70) {
        percentElem.classList.add('kpi-neutral');
    } else {
        percentElem.classList.add('kpi-positive');
    }

    // Update remaining budget status
    const remainingStatus = document.getElementById('remainingBudgetStatus');
    if (remainingBudget <= 0) {
        remainingStatus.textContent = 'Budget depleted';
        remainingStatus.className = 'text-muted kpi-negative';
    } else if (remainingBudget < totalBudget * 0.1) {
        remainingStatus.textContent = 'Low remaining budget';
        remainingStatus.className = 'text-muted kpi-neutral';
    } else {
        remainingStatus.textContent = 'Available to spend';
        remainingStatus.className = 'text-muted';
    }

    // Determine spending trend (if we have the data to do so)
    // In a real implementation, you would calculate this from monthly data
    document.getElementById('spendingTrend').textContent = 'Stable';
    document.getElementById('spendingTrendDesc').textContent = 'Based on current data';
}

/**
 * Load overview chart (Fiscal Year Trend)
 */
function loadOverviewChart() {
    // Show loading, hide chart and error
    document.getElementById('overviewLoading').style.display = 'flex';
    document.getElementById('overviewChartContainer').style.display = 'none';
    document.getElementById('overviewChartError').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query string with proper handling of empty values
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    if (department) queryParams.push('department=' + encodeURIComponent(department));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL
    const url = '/groups/finance/budget/api/chart-data?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Check if we have data
                if (data.fiscal_years && data.fiscal_years.length > 0) {
                    // Render the chart
                    createOverviewChart(data.fiscal_years, data.amended_totals);

                    // Show chart, hide loading
                    document.getElementById('overviewLoading').style.display = 'none';
                    document.getElementById('overviewChartContainer').style.display = 'block';
                } else {
                    // No data to display
                    document.getElementById('overviewLoading').style.display = 'none';
                    document.getElementById('overviewChartError').style.display = 'block';
                    document.getElementById('overviewErrorMessage').textContent =
                        'No budget data available for the selected filters. Try different criteria.';
                }
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);

            // Show error message
            document.getElementById('overviewErrorMessage').textContent = error.message;
            document.getElementById('overviewChartError').style.display = 'block';
            document.getElementById('overviewLoading').style.display = 'none';
        });
}

/**
 * Create the overview chart (Fiscal Year Trend)
 * @param {Array} fiscalYears - Array of fiscal years
 * @param {Array} budgetValues - Array of budget values
 */
function createOverviewChart(fiscalYears, budgetValues) {
    // Verify Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly!');
        document.getElementById('overviewErrorMessage').textContent = 'Chart.js library not loaded. Please try refreshing the page.';
        document.getElementById('overviewChartError').style.display = 'block';
        document.getElementById('overviewLoading').style.display = 'none';
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('budgetChart');
    if (!canvas) {
        console.error('Canvas element "budgetChart" not found');
        return;
    }

    // Properly destroy any existing chart
    try {
        // Try Chart.js v3+ method first
        if (typeof Chart.getChart === 'function') {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
        }
        // Fall back to our stored reference
        else if (chartInstances.overview) {
            chartInstances.overview.destroy();
        }
    } catch (e) {
        console.warn('Error destroying existing chart:', e);
    }

    // Format numbers for tooltip and Y axis
    const formatCurrency = function (value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const lineColor = isDarkMode ? '#6FA3FF' : '#0D3B66';
    const pointColor = isDarkMode ? '#6FA3FF' : '#0D3B66';
    const pointHoverColor = isDarkMode ? '#FFFFFF' : '#0D3B66';

    // Create new chart
    try {
        // Calculate moving average if we have enough data points
        let movingAverageData = null;
        if (budgetValues.length >= 3) {
            movingAverageData = calculateMovingAverage(budgetValues, 2);
        }

        chartInstances.overview = new Chart(canvas, {
            type: 'line',
            data: {
                labels: fiscalYears,
                datasets: [
                    {
                        label: 'Amended Budget',
                        data: budgetValues,
                        backgroundColor: 'rgba(13, 59, 102, 0.2)',
                        borderColor: lineColor,
                        borderWidth: 3,
                        pointBackgroundColor: pointColor,
                        pointBorderColor: pointColor,
                        pointHoverBackgroundColor: pointHoverColor,
                        pointHoverBorderColor: pointHoverColor,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        fill: true,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Amended Budget Total by Fiscal Year',
                        color: textColor,
                        font: {
                            size: 18,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: textColor
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return formatCurrency(context.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Fiscal Year',
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Amended Budget Total ($)',
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });

        // Add trend line if we have moving average data
        if (movingAverageData) {
            chartInstances.overview.data.datasets.push({
                label: 'Trend (2-Year Moving Avg)',
                data: movingAverageData,
                borderColor: isDarkMode ? 'rgba(255, 183, 77, 1)' : 'rgba(255, 152, 0, 1)',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false,
                tension: 0
            });
            chartInstances.overview.update();
        }

    } catch (error) {
        console.error('Error creating chart:', error);
        document.getElementById('overviewErrorMessage').textContent = 'Error creating chart: ' + error.message;
        document.getElementById('overviewChartError').style.display = 'block';
        document.getElementById('overviewLoading').style.display = 'none';
    }
}

/**
 * Load department breakdown chart
 */
function loadDepartmentChart() {
    // Show loading, hide chart
    document.getElementById('departmentChartLoading').style.display = 'flex';
    document.getElementById('departmentChartContainer').style.display = 'none';
    document.getElementById('topDepartmentsLoading').style.display = 'block';
    document.getElementById('topDepartmentsList').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;

    // Build query string
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL for budget summary API
    const url = '/groups/finance/budget/api/budget-summary?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.length > 0) {
                createDepartmentChart(data.data);
                updateTopDepartmentsList(data.data);

                // Show charts, hide loading
                document.getElementById('departmentChartLoading').style.display = 'none';
                document.getElementById('departmentChartContainer').style.display = 'block';
                document.getElementById('topDepartmentsLoading').style.display = 'none';
                document.getElementById('topDepartmentsList').style.display = 'block';
            } else {
                throw new Error(data.error || 'No data available for the selected filters');
            }
        })
        .catch(error => {
            console.error('Error loading department data:', error);
            // Show error in charts
            document.getElementById('departmentChartLoading').style.display = 'none';
            document.getElementById('topDepartmentsLoading').style.display = 'none';

            // Create error messages
            const errorMsgEl = document.createElement('div');
            errorMsgEl.className = 'alert alert-warning mt-3';
            errorMsgEl.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;

            document.getElementById('departmentChartContainer').innerHTML = '';
            document.getElementById('departmentChartContainer').appendChild(errorMsgEl.cloneNode(true));
            document.getElementById('departmentChartContainer').style.display = 'block';

            document.getElementById('topDepartmentsList').innerHTML = '';
            document.getElementById('topDepartmentsList').appendChild(errorMsgEl.cloneNode(true));
            document.getElementById('topDepartmentsList').style.display = 'block';
        });
}

/**
 * Create department breakdown chart
 * @param {Array} data - Budget summary data by department
 */
function createDepartmentChart(data) {
    if (!data || !data.length) return;

    // Group data by department and calculate totals
    const departmentData = {};

    data.forEach(item => {
        if (!item.department) return;

        // Check if department exists in our map
        if (!departmentData[item.department]) {
            departmentData[item.department] = {
                budget: 0,
                actual: 0,
                encumbrance: 0,
                remaining: 0
            };
        }

        // Add to totals
        departmentData[item.department].budget += item.total_budget;
        departmentData[item.department].actual += item.total_actual;
        departmentData[item.department].encumbrance += item.total_encumbrance;
        departmentData[item.department].remaining += item.remaining_budget;
    });

    // Sort departments by budget and get top departments
    const sortedDepartments = Object.keys(departmentData)
        .sort((a, b) => departmentData[b].budget - departmentData[a].budget);

    // Limit to top 8 departments and combine others
    const labels = [];
    const budgetValues = [];
    const actualValues = [];

    let otherBudget = 0;
    let otherActual = 0;

    sortedDepartments.forEach((dept, index) => {
        if (index < 7) {
            labels.push(dept);
            budgetValues.push(departmentData[dept].budget);
            actualValues.push(departmentData[dept].actual);
        } else {
            otherBudget += departmentData[dept].budget;
            otherActual += departmentData[dept].actual;
        }
    });

    // Add "Other" category if needed
    if (otherBudget > 0) {
        labels.push('Other Departments');
        budgetValues.push(otherBudget);
        actualValues.push(otherActual);
    }

    // Get canvas element
    const canvas = document.getElementById('departmentChart');
    if (!canvas) {
        console.error('Canvas element "departmentChart" not found');
        return;
    }

    // Properly destroy any existing chart
    try {
        if (typeof Chart.getChart === 'function') {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
        } else if (chartInstances.department) {
            chartInstances.department.destroy();
        }
    } catch (e) {
        console.warn('Error destroying existing chart:', e);
    }

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Chart colors
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Colors for departments
    const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(100, 120, 140, 0.7)'
    ];

    const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));

    // Create chart
    try {
        chartInstances.department = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Budget Allocation',
                    data: budgetValues,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Budget Allocation by Department',
                        color: textColor,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            color: textColor,
                            boxWidth: 15,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const value = context.raw;
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating department chart:', error);
        document.getElementById('departmentChartContainer').innerHTML =
            `<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error creating chart: ${error.message}</div>`;
    }
}

/**
 * Update top departments list
 * @param {Array} data - Budget summary data
 */
function updateTopDepartmentsList(data) {
    if (!data || !data.length) return;

    // Group data by department
    const departmentData = {};

    data.forEach(item => {
        if (!item.department) return;

        if (!departmentData[item.department]) {
            departmentData[item.department] = {
                budget: 0,
                actual: 0,
                percent: 0
            };
        }

        departmentData[item.department].budget += item.total_budget;
        departmentData[item.department].actual += item.total_actual;
    });

    // Calculate percent spent
    Object.keys(departmentData).forEach(dept => {
        if (departmentData[dept].budget > 0) {
            departmentData[dept].percent = (departmentData[dept].actual / departmentData[dept].budget) * 100;
        }
    });

    // Sort departments by budget amount
    const sortedDepartments = Object.keys(departmentData)
        .sort((a, b) => departmentData[b].budget - departmentData[a].budget)
        .slice(0, 5); // Get top 5

    // Get list element
    const listEl = document.getElementById('topDepartmentsList');
    listEl.innerHTML = '';

    // Create list items
    sortedDepartments.forEach(dept => {
        const item = document.createElement('li');
        item.className = 'list-group-item d-flex justify-content-between align-items-center';

        const percentClass = departmentData[dept].percent > 90 ? 'bg-danger' :
            departmentData[dept].percent > 70 ? 'bg-warning' : 'bg-success';

        item.innerHTML = `
            <div>
                <strong>${dept}</strong>
                <div class="text-muted small">${formatCurrency(departmentData[dept].budget)}</div>
            </div>
            <span class="badge ${percentClass} rounded-pill">${departmentData[dept].percent.toFixed(1)}%</span>
        `;

        listEl.appendChild(item);
    });

    // Add a heading
    const fiscalYear = document.getElementById('fiscalYearSelect').value || 'All Years';
    const heading = document.createElement('li');
    heading.className = 'list-group-item bg-light';
    heading.innerHTML = `<strong>Top Departments (${fiscalYear})</strong>`;
    listEl.insertBefore(heading, listEl.firstChild);
}

/**
 * Load monthly trend chart
 */
function loadMonthlyChart() {
    // Show loading indicator
    document.getElementById('monthlyChartLoading').style.display = 'flex';
    document.getElementById('monthlyChartContainer').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query parameters
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    if (department) queryParams.push('department=' + encodeURIComponent(department));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL
    const url = '/groups/finance/budget/api/monthly-trend?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.length > 0) {
                createMonthlyTrendChart(data.data);

                // Show chart, hide loading
                document.getElementById('monthlyChartLoading').style.display = 'none';
                document.getElementById('monthlyChartContainer').style.display = 'block';
            } else {
                throw new Error(data.error || 'No monthly data available for the selected filters');
            }
        })
        .catch(error => {
            console.error('Error loading monthly data:', error);

            // Show error message
            document.getElementById('monthlyChartLoading').style.display = 'none';

            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-warning mt-3';
            errorMsg.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;

            document.getElementById('monthlyChartContainer').innerHTML = '';
            document.getElementById('monthlyChartContainer').appendChild(errorMsg);
            document.getElementById('monthlyChartContainer').style.display = 'block';
        });
}

/**
 * Create monthly trend chart
 * @param {Array} data - Monthly trend data
 */
function createMonthlyTrendChart(data) {
    if (!data || !data.length) return;

    // Sort data by month number
    data.sort((a, b) => a.month_num - b.month_num);

    // Extract chart data
    const labels = data.map(item => item.month);
    const monthlyActual = data.map(item => item.monthly_actual);
    const monthlyBudget = data.map(item => item.monthly_budget);
    const runningActual = data.map(item => item.running_actual);

    // Get canvas element
    const canvas = document.getElementById('monthlyTrendChart');
    if (!canvas) {
        console.error('Canvas element "monthlyTrendChart" not found');
        return;
    }

    // Destroy existing chart if any
    try {
        if (typeof Chart.getChart === 'function') {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
        } else if (chartInstances.monthly) {
            chartInstances.monthly.destroy();
        }
    } catch (e) {
        console.warn('Error destroying existing chart:', e);
    }

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Chart colors
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Create the chart
    try {
        chartInstances.monthly = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Monthly Actual',
                        data: monthlyActual,
                        backgroundColor: isDarkMode ? 'rgba(75, 192, 192, 0.7)' : 'rgba(54, 162, 235, 0.7)',
                        borderColor: isDarkMode ? 'rgba(75, 192, 192, 1)' : 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Monthly Budget',
                        data: monthlyBudget,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Running Total',
                        data: runningActual,
                        type: 'line',
                        backgroundColor: 'transparent',
                        borderColor: isDarkMode ? 'rgba(255, 99, 132, 1)' : 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: isDarkMode ? 'rgba(255, 99, 132, 1)' : 'rgba(255, 99, 132, 1)',
                        pointRadius: 4,
                        fill: false,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Budget vs. Actual Spending',
                        color: textColor,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.dataset.label || '';
                                const value = context.raw;
                                return `${label}: ${formatCurrency(value)}`;
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
                        title: {
                            display: true,
                            text: 'Monthly Amount',
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return formatCurrency(value);
                            }
                        }
                    },
                    y1: {
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Running Total',
                            color: textColor
                        },
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating monthly chart:', error);
        document.getElementById('monthlyChartContainer').innerHTML =
            `<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error creating chart: ${error.message}</div>`;
    }
}

/**
 * Load budget vs actual comparison chart
 */
function loadComparisonChart() {
    // Show loading indicator
    document.getElementById('comparisonChartLoading').style.display = 'flex';
    document.getElementById('comparisonChartContainer').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query parameters
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    if (department) queryParams.push('department=' + encodeURIComponent(department));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL for budget summary API
    const url = '/groups/finance/budget/api/budget-summary?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success && data.data && data.data.length > 0) {
                createComparisonChart(data.data);

                // Show chart, hide loading
                document.getElementById('comparisonChartLoading').style.display = 'none';
                document.getElementById('comparisonChartContainer').style.display = 'block';
            } else {
                throw new Error(data.error || 'No data available for the selected filters');
            }
        })
        .catch(error => {
            console.error('Error loading comparison data:', error);

            // Show error message
            document.getElementById('comparisonChartLoading').style.display = 'none';

            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-warning mt-3';
            errorMsg.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;

            document.getElementById('comparisonChartContainer').innerHTML = '';
            document.getElementById('comparisonChartContainer').appendChild(errorMsg);
            document.getElementById('comparisonChartContainer').style.display = 'block';
        });
}

/**
 * Create budget vs actual comparison chart
 * @param {Array} data - Budget summary data
 */
function createComparisonChart(data) {
    if (!data || !data.length) return;

    // Group data by department and calculate totals
    const departmentData = {};

    data.forEach(item => {
        if (!item.department) return;

        if (!departmentData[item.department]) {
            departmentData[item.department] = {
                budget: 0,
                actual: 0,
                encumbrance: 0,
                remaining: 0
            };
        }

        departmentData[item.department].budget += item.total_budget;
        departmentData[item.department].actual += item.total_actual;
        departmentData[item.department].encumbrance += item.total_encumbrance;
        departmentData[item.department].remaining += item.remaining_budget;
    });

    // Sort departments by budget and get top departments
    const sortedDepartments = Object.keys(departmentData)
        .sort((a, b) => departmentData[b].budget - departmentData[a].budget)
        .slice(0, 6); // Show top 6 departments only

    // Extract chart data
    const labels = sortedDepartments;
    const budgetValues = sortedDepartments.map(dept => departmentData[dept].budget);
    const actualValues = sortedDepartments.map(dept => departmentData[dept].actual);
    const encumbranceValues = sortedDepartments.map(dept => departmentData[dept].encumbrance);

    // Get canvas element
    const canvas = document.getElementById('budgetVsActualChart');
    if (!canvas) {
        console.error('Canvas element "budgetVsActualChart" not found');
        return;
    }

    // Destroy existing chart if any
    try {
        if (typeof Chart.getChart === 'function') {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
        } else if (chartInstances.comparison) {
            chartInstances.comparison.destroy();
        }
    } catch (e) {
        console.warn('Error destroying existing chart:', e);
    }

    // Determine if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Chart colors
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Create the chart
    try {
        chartInstances.comparison = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Budget',
                        data: budgetValues,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Actual',
                        data: actualValues,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Encumbrance',
                        data: encumbranceValues,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                indexAxis: 'y', // Horizontal bar chart
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Budget vs. Actual by Department',
                        color: textColor,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.dataset.label || '';
                                const value = context.raw;
                                return `${label}: ${formatCurrency(value)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: false,
                        title: {
                            display: true,
                            text: 'Amount',
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return formatCurrency(value);
                            }
                        }
                    },
                    y: {
                        stacked: false,
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating comparison chart:', error);
        document.getElementById('comparisonChartContainer').innerHTML =
            `<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error creating chart: ${error.message}</div>`;
    }
}

/**
 * Load budget summary data and populate table
 */
function loadBudgetSummary() {
    // Show loading indicator
    document.getElementById('budgetSummaryLoading').style.display = 'block';
    document.getElementById('budgetSummaryContainer').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query string
    let queryParams = [];
    if (fiscalYear) queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    if (department) queryParams.push('department=' + encodeURIComponent(department));

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL
    const url = '/groups/finance/budget/api/budget-summary?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Populate table
                populateBudgetSummaryTable(data.data);

                // Show table, hide loading
                document.getElementById('budgetSummaryLoading').style.display = 'none';
                document.getElementById('budgetSummaryContainer').style.display = 'block';
            } else {