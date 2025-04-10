/**
 * Budget Dashboard JavaScript
 * 
 * This file handles the interactive functionality for the Budget Dashboard,
 * including loading data, initializing charts, and handling user interactions.
 */

// Document ready function
document.addEventListener('DOMContentLoaded', function () {
    // Initialize event handlers
    document.getElementById('applyFilters').addEventListener('click', loadChartData);
    document.getElementById('retryButton').addEventListener('click', function () {
        document.getElementById('chartError').style.display = 'none';
        loadChartData();
    });

    // Load chart when page is ready
    loadChartData();

    // Apply initial theme to page
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    updatePageTheme(isDarkMode);

    // Add resize listener
    window.addEventListener('resize', function () {
        if (window.budgetChart) {
            window.budgetChart.resize();
        }
    });

    // Listen for dark mode changes
    document.addEventListener('darkModeChanged', function () {
        updateChartTheme();
    });

    // Add event listener for theme toggle
    const themeToggle = document.getElementById('toggle-theme');
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            // Small delay to allow DOM to update
            setTimeout(function () {
                const isDarkMode = document.documentElement.classList.contains('dark-mode');
                updatePageTheme(isDarkMode);
                updateChartTheme();
            }, 100);
        });
    }
});

/**
 * Load chart data from API
 */
function loadChartData() {
    // Show loading, hide chart and error
    document.getElementById('chartLoading').style.display = 'flex';
    document.getElementById('chartContainer').style.display = 'none';
    document.getElementById('chartError').style.display = 'none';
    document.getElementById('statsSection').style.display = 'none';

    // Get filter values
    const fiscalYear = document.getElementById('fiscalYearSelect').value;
    const department = document.getElementById('departmentSelect').value;

    // Build query string with proper handling of empty values
    let queryParams = [];
    if (fiscalYear && fiscalYear !== '') {
        queryParams.push('fiscal_year=' + encodeURIComponent(fiscalYear));
    }
    if (department && department !== '') {
        queryParams.push('department=' + encodeURIComponent(department));
    }

    // Add timestamp to prevent caching
    queryParams.push('_t=' + new Date().getTime());

    // Build URL
    const url = '/groups/finance/budget/api/chart-data?' + queryParams.join('&');

    // Fetch the data
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Check if we have data
                if (data.fiscal_years && data.fiscal_years.length > 0) {
                    // Render the chart
                    createBudgetChart(data.fiscal_years, data.amended_totals);

                    // Show chart, hide loading
                    document.getElementById('chartLoading').style.display = 'none';
                    document.getElementById('chartContainer').style.display = 'block';
                } else {
                    // No data to display
                    document.getElementById('chartLoading').style.display = 'none';
                    document.getElementById('chartError').style.display = 'block';
                    document.getElementById('errorMessage').textContent =
                        'No budget data available for the selected filters. Try different criteria.';
                }
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);

            // Show error message
            document.getElementById('errorMessage').textContent = error.message;
            document.getElementById('chartError').style.display = 'block';
            document.getElementById('chartLoading').style.display = 'none';
        });
}

/**
 * Create the budget chart using Chart.js
 * @param {Array} fiscal_years - Array of fiscal years
 * @param {Array} budget_values - Array of budget values
 */
function createBudgetChart(fiscal_years, budget_values) {
    // Verify Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded properly!');
        document.getElementById('errorMessage').textContent = 'Chart.js library not loaded. Please try refreshing the page.';
        document.getElementById('chartError').style.display = 'block';
        document.getElementById('chartLoading').style.display = 'none';
        return;
    }

    // Get canvas element
    const canvas = document.getElementById('budgetChart');
    if (!canvas) {
        console.error('Canvas element "budgetChart" not found');
        return;
    }

    // Get 2d context
    const ctx = canvas.getContext('2d');

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
        else if (window.budgetChart && typeof window.budgetChart.destroy === 'function') {
            window.budgetChart.destroy();
        }
    } catch (e) {
        console.warn('Error destroying existing chart:', e);
        // Continue anyway since we'll override it
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
        window.budgetChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: fiscal_years,
                datasets: [{
                    label: 'Amended Budget',
                    data: budget_values,
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
                }]
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

        // After successful chart creation, show summary stats
        updateSummaryStats(fiscal_years, budget_values);
        document.getElementById('statsSection').style.display = 'flex';

    } catch (error) {
        console.error('Error creating chart:', error);
        document.getElementById('errorMessage').textContent = 'Error creating chart: ' + error.message;
        document.getElementById('chartError').style.display = 'block';
        document.getElementById('chartLoading').style.display = 'none';
    }
}

/**
 * Update summary statistics based on chart data
 * @param {Array} years - Array of fiscal years
 * @param {Array} values - Array of budget values
 */
function updateSummaryStats(years, values) {
    if (!years || !values || years.length === 0 || values.length === 0) {
        return;
    }

    // Calculate average budget
    const sum = values.reduce((acc, val) => acc + val, 0);
    const average = sum / values.length;

    // Format and display average
    document.getElementById('averageBudget').textContent =
        new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(average);

    // Calculate growth trend if we have at least 2 years of data
    if (values.length >= 2) {
        const firstValue = values[0];
        const lastValue = values[values.length - 1];

        // Calculate compound annual growth rate if spanning multiple years
        if (years.length > 1) {
            const yearDiff = years[years.length - 1] - years[0];
            const growthRate = Math.pow(lastValue / firstValue, 1 / yearDiff) - 1;

            // Format as percentage with appropriate sign
            const formattedGrowth = (growthRate * 100).toFixed(1) + '%';
            document.getElementById('growthTrend').textContent =
                (growthRate >= 0 ? '+' : '') + formattedGrowth;

            // Add color based on growth direction
            document.getElementById('growthTrend').style.color =
                growthRate >= 0 ? 'var(--success-color)' : 'var(--danger-color)';
        } else {
            document.getElementById('growthTrend').textContent = 'N/A';
        }
    } else {
        document.getElementById('growthTrend').textContent = 'N/A';
    }

    // Display data point count
    document.getElementById('dataPointCount').textContent = years.length;
}

/**
 * Update the chart theme based on dark/light mode
 */
function updateChartTheme() {
    if (!window.budgetChart) {
        return;
    }

    const isDarkMode = document.documentElement.classList.contains('dark-mode');

    // Define chart colors based on mode
    const textColor = isDarkMode ? '#E0E0E0' : '#333333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const lineColor = isDarkMode ? '#6FA3FF' : '#0D3B66';
    const pointColor = isDarkMode ? '#6FA3FF' : '#0D3B66';

    // Update dataset colors
    window.budgetChart.data.datasets[0].borderColor = lineColor;
    window.budgetChart.data.datasets[0].pointBackgroundColor = pointColor;
    window.budgetChart.data.datasets[0].pointBorderColor = pointColor;

    // Update title and legend text colors
    if (window.budgetChart.options.plugins.title) {
        window.budgetChart.options.plugins.title.color = textColor;
    }

    if (window.budgetChart.options.plugins.legend && window.budgetChart.options.plugins.legend.labels) {
        window.budgetChart.options.plugins.legend.labels.color = textColor;
    }

    // Update scales
    if (window.budgetChart.options.scales.x) {
        window.budgetChart.options.scales.x.grid.color = gridColor;
        window.budgetChart.options.scales.x.ticks.color = textColor;
        if (window.budgetChart.options.scales.x.title) {
            window.budgetChart.options.scales.x.title.color = textColor;
        }
    }

    if (window.budgetChart.options.scales.y) {
        window.budgetChart.options.scales.y.grid.color = gridColor;
        window.budgetChart.options.scales.y.ticks.color = textColor;
        if (window.budgetChart.options.scales.y.title) {
            window.budgetChart.options.scales.y.title.color = textColor;
        }
    }

    // Update the chart
    window.budgetChart.update();

    // Update page elements styling for theme
    updatePageTheme(isDarkMode);
}

/**
 * Update page elements styling for the current theme
 * @param {boolean} isDarkMode - Whether dark mode is active
 */
function updatePageTheme(isDarkMode) {
    // Update stats cards
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        if (isDarkMode) {
            card.classList.add('bg-dark');
            card.classList.add('text-light');
        } else {
            card.classList.remove('bg-dark');
            card.classList.remove('text-light');
        }
    });

    // You can add more element-specific theme updates here if needed
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