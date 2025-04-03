/**
 * Chart.js Theme Helper
 * 
 * This script helps manage Chart.js themes for dark/light mode.
 * It centralizes color management for charts across the application.
 * Compatible with Chart.js v2.x, v3.x, and v4.x
 */

class ChartThemeHelper {
    constructor() {
        this.isDarkMode = document.documentElement.classList.contains('dark-mode');
        this.setupThemes();
        this.setupListeners();
    }

    /**
     * Set up the light and dark theme palettes
     */
    setupThemes() {
        // Color palettes
        this.lightPalette = {
            primary: '#4361ee',
            secondary: '#4cc9f0',
            accent: '#f72585',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            background: '#ffffff',
            text: '#5c5f73',
            gridLines: 'rgba(0, 0, 0, 0.1)',
            datasets: [
                'rgba(67, 97, 238, 0.7)',   // primary
                'rgba(76, 201, 240, 0.7)',  // secondary
                'rgba(247, 37, 133, 0.7)',  // accent
                'rgba(16, 185, 129, 0.7)',  // success
                'rgba(245, 158, 11, 0.7)',  // warning
                'rgba(239, 68, 68, 0.7)'    // danger
            ],
            borderColors: [
                'rgba(67, 97, 238, 1)',    // primary
                'rgba(76, 201, 240, 1)',   // secondary
                'rgba(247, 37, 133, 1)',   // accent
                'rgba(16, 185, 129, 1)',   // success
                'rgba(245, 158, 11, 1)',   // warning
                'rgba(239, 68, 68, 1)'     // danger
            ]
        };

        this.darkPalette = {
            primary: '#6d87ff',
            secondary: '#62dbff',
            accent: '#ff5fa8',
            success: '#34d399',
            warning: '#fbbf24',
            danger: '#f87171',
            background: '#1e293b',
            text: '#cbd5e1',
            gridLines: 'rgba(255, 255, 255, 0.1)',
            datasets: [
                'rgba(109, 135, 255, 0.7)',  // primary
                'rgba(98, 219, 255, 0.7)',   // secondary
                'rgba(255, 95, 168, 0.7)',   // accent
                'rgba(52, 211, 153, 0.7)',   // success
                'rgba(251, 191, 36, 0.7)',   // warning
                'rgba(248, 113, 113, 0.7)'   // danger
            ],
            borderColors: [
                'rgba(109, 135, 255, 1)',   // primary
                'rgba(98, 219, 255, 1)',    // secondary
                'rgba(255, 95, 168, 1)',    // accent
                'rgba(52, 211, 153, 1)',    // success
                'rgba(251, 191, 36, 1)',    // warning
                'rgba(248, 113, 113, 1)'    // danger
            ]
        };

        // Currently active palette
        this.activePalette = this.isDarkMode ? this.darkPalette : this.lightPalette;
    }

    /**
     * Set up event listeners for theme changes
     */
    setupListeners() {
        // Listen for dark mode toggle
        document.addEventListener('DOMContentLoaded', () => {
            const themeToggle = document.getElementById('toggle-theme');
            if (themeToggle) {
                themeToggle.addEventListener('click', () => {
                    // Delay to allow the DOM to update first
                    setTimeout(() => {
                        this.isDarkMode = document.documentElement.classList.contains('dark-mode');
                        this.activePalette = this.isDarkMode ? this.darkPalette : this.lightPalette;
                        this.updateAllCharts();
                    }, 50);
                });
            }
        });

        // Observe class changes on the HTML element
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        const newIsDarkMode = document.documentElement.classList.contains('dark-mode');
                        if (newIsDarkMode !== this.isDarkMode) {
                            this.isDarkMode = newIsDarkMode;
                            this.activePalette = this.isDarkMode ? this.darkPalette : this.lightPalette;
                            this.updateAllCharts();
                        }
                    }
                });
            });

            observer.observe(document.documentElement, { attributes: true });
        }
    }

    /**
     * Get all Chart.js instances safely across different versions
     * @returns {Array} Array of Chart instances
     */
    getAllChartInstances() {
        if (typeof Chart === 'undefined') return [];

        try {
            const charts = [];

            // For Chart.js v4.x
            if (typeof Chart.getChart === 'function') {
                const canvases = document.querySelectorAll('canvas');
                canvases.forEach(canvas => {
                    try {
                        const chart = Chart.getChart(canvas);
                        if (chart) {
                            charts.push(chart);
                        }
                    } catch (e) {
                        // Skip canvases without charts
                    }
                });

                if (charts.length > 0) {
                    return charts;
                }
            }

            // For Chart.js v3+
            if (Chart.instances) {
                // If it's a Map (Chart.js v3+)
                if (Chart.instances instanceof Map) {
                    return Array.from(Chart.instances.values());
                }
                // If it's an object (some versions)
                else if (typeof Chart.instances === 'object') {
                    return Object.values(Chart.instances);
                }
            }

            // For Chart.js v2.x
            if (Chart.instances && Array.isArray(Chart.instances)) {
                return Chart.instances;
            }

            // No instances found or unsupported version
            return [];
        } catch (error) {
            console.warn('Error getting Chart instances:', error);
            return [];
        }
    }

    /**
     * Update all Chart.js instances on the page
     */
    updateAllCharts() {
        if (typeof Chart === 'undefined') return;

        // Get all chart instances
        const chartInstances = this.getAllChartInstances();

        // Update each chart
        chartInstances.forEach(chart => {
            try {
                this.updateChartTheme(chart);
            } catch (error) {
                console.warn('Error updating individual chart:', error);
            }
        });
    }

    /**
     * Update a specific chart's theme
     * @param {Chart} chart - The Chart.js instance to update
     */
    updateChartTheme(chart) {
        if (!chart || !chart.options) return;

        try {
            // FIX: Create a new options object instead of modifying existing one to avoid recursive updates
            const newOptions = JSON.parse(JSON.stringify(chart.options));
            let needsUpdate = false;

            // Chart.js v3.x/v4.x structure
            if (newOptions.plugins) {
                // Update legend text color
                if (newOptions.plugins.legend && newOptions.plugins.legend.labels) {
                    newOptions.plugins.legend.labels.color = this.activePalette.text;
                    needsUpdate = true;
                }

                // Update title color
                if (newOptions.plugins.title) {
                    newOptions.plugins.title.color = this.activePalette.text;
                    needsUpdate = true;
                }
            }

            // Chart.js v2.x structure
            if (newOptions.legend && newOptions.legend.labels) {
                newOptions.legend.labels.fontColor = this.activePalette.text;
                needsUpdate = true;
            }

            if (newOptions.title) {
                newOptions.title.fontColor = this.activePalette.text;
                needsUpdate = true;
            }

            // Update scales (works for both v2.x and v3.x/v4.x with different structures)
            if (newOptions.scales) {
                // v3.x/v4.x structure
                if (newOptions.scales.x) {
                    if (newOptions.scales.x.ticks) {
                        newOptions.scales.x.ticks.color = this.activePalette.text;
                        needsUpdate = true;
                    }
                    if (newOptions.scales.x.grid) {
                        newOptions.scales.x.grid.color = this.activePalette.gridLines;
                        needsUpdate = true;
                    }
                    if (newOptions.scales.x.title) {
                        newOptions.scales.x.title.color = this.activePalette.text;
                        needsUpdate = true;
                    }
                }

                if (newOptions.scales.y) {
                    if (newOptions.scales.y.ticks) {
                        newOptions.scales.y.ticks.color = this.activePalette.text;
                        needsUpdate = true;
                    }
                    if (newOptions.scales.y.grid) {
                        newOptions.scales.y.grid.color = this.activePalette.gridLines;
                        needsUpdate = true;
                    }
                    if (newOptions.scales.y.title) {
                        newOptions.scales.y.title.color = this.activePalette.text;
                        needsUpdate = true;
                    }
                }

                // v2.x structure
                if (Array.isArray(newOptions.scales.xAxes)) {
                    newOptions.scales.xAxes.forEach(axis => {
                        if (axis.ticks) {
                            axis.ticks.fontColor = this.activePalette.text;
                            needsUpdate = true;
                        }
                        if (axis.gridLines) {
                            axis.gridLines.color = this.activePalette.gridLines;
                            needsUpdate = true;
                        }
                    });
                }

                if (Array.isArray(newOptions.scales.yAxes)) {
                    newOptions.scales.yAxes.forEach(axis => {
                        if (axis.ticks) {
                            axis.ticks.fontColor = this.activePalette.text;
                            needsUpdate = true;
                        }
                        if (axis.gridLines) {
                            axis.gridLines.color = this.activePalette.gridLines;
                            needsUpdate = true;
                        }
                    });
                }
            }

            // For pie/doughnut charts, update background colors if needed
            if (chart.config && chart.data && chart.data.datasets &&
                (chart.config.type === 'pie' || chart.config.type === 'doughnut')) {
                // Only update if colors weren't explicitly defined by user
                if (!chart.data._userDefinedColors) {
                    // Create a new copy of the datasets to avoid direct modification
                    const newDatasets = JSON.parse(JSON.stringify(chart.data.datasets));
                    newDatasets[0].backgroundColor = this.activePalette.datasets;
                    newDatasets[0].borderColor = this.activePalette.borderColors;

                    // Set datasets directly during the update instead of modifying them
                    needsUpdate = true;
                }
            }

            // Update the chart with new options only if changes were made
            if (needsUpdate && typeof chart.update === 'function') {
                // Use update with entirely new configuration to avoid recursion
                chart.update({
                    options: newOptions
                });
            }
        } catch (error) {
            console.warn('Error updating chart theme:', error);
        }
    }

    /**
     * Get chart colors for current theme
     * @param {number} count - Number of colors needed
     * @param {boolean} withOpacity - Whether to include opacity
     * @returns {Array} Array of colors
     */
    getChartColors(count = 6, withOpacity = true) {
        const colors = withOpacity ?
            this.activePalette.datasets.slice(0, count) :
            this.activePalette.borderColors.slice(0, count);

        // If we need more colors than we have, cycle through them
        if (count > colors.length) {
            const extraCount = count - colors.length;
            for (let i = 0; i < extraCount; i++) {
                colors.push(colors[i % colors.length]);
            }
        }

        return colors;
    }

    /**
     * Get default chart options for the current theme
     * @param {string} type - Chart type ('bar', 'line', 'pie', etc)
     * @returns {Object} Chart options
     */
    getChartOptions(type = 'bar') {
        // Detect Chart.js version
        const isV3 = typeof Chart !== 'undefined' && Chart.defaults && Chart.defaults.color !== undefined;

        // Base options structure for v3/v4
        if (isV3) {
            const baseOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: this.activePalette.text,
                            font: {
                                family: "'Roboto', sans-serif"
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                            family: "'Roboto', sans-serif"
                        },
                        bodyFont: {
                            family: "'Roboto', sans-serif"
                        },
                        backgroundColor: this.isDarkMode ? '#334155' : 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.activePalette.gridLines,
                        borderWidth: 1
                    }
                }
            };

            // Add type-specific options for v3/v4
            switch (type) {
                case 'bar':
                case 'line':
                    return {
                        ...baseOptions,
                        scales: {
                            x: {
                                grid: {
                                    color: this.activePalette.gridLines
                                },
                                ticks: {
                                    color: this.activePalette.text,
                                    font: {
                                        family: "'Roboto', sans-serif"
                                    }
                                }
                            },
                            y: {
                                grid: {
                                    color: this.activePalette.gridLines
                                },
                                ticks: {
                                    color: this.activePalette.text,
                                    font: {
                                        family: "'Roboto', sans-serif"
                                    }
                                },
                                title: {
                                    display: false,
                                    color: this.activePalette.text
                                },
                                beginAtZero: true
                            }
                        }
                    };
                case 'pie':
                case 'doughnut':
                    return baseOptions;
                default:
                    return baseOptions;
            }
        }
        // Base options structure for v2
        else {
            const baseOptions = {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    labels: {
                        fontColor: this.activePalette.text,
                        fontFamily: "'Roboto', sans-serif"
                    }
                },
                tooltips: {
                    titleFontFamily: "'Roboto', sans-serif",
                    bodyFontFamily: "'Roboto', sans-serif",
                    backgroundColor: this.isDarkMode ? '#334155' : 'rgba(0, 0, 0, 0.8)',
                    titleFontColor: '#ffffff',
                    bodyFontColor: '#ffffff',
                    borderColor: this.activePalette.gridLines,
                    borderWidth: 1
                }
            };

            // Add type-specific options for v2
            switch (type) {
                case 'bar':
                case 'line':
                    return {
                        ...baseOptions,
                        scales: {
                            xAxes: [{
                                gridLines: {
                                    color: this.activePalette.gridLines
                                },
                                ticks: {
                                    fontColor: this.activePalette.text,
                                    fontFamily: "'Roboto', sans-serif"
                                }
                            }],
                            yAxes: [{
                                gridLines: {
                                    color: this.activePalette.gridLines
                                },
                                ticks: {
                                    fontColor: this.activePalette.text,
                                    fontFamily: "'Roboto', sans-serif",
                                    beginAtZero: true
                                }
                            }]
                        }
                    };
                case 'pie':
                case 'doughnut':
                    return baseOptions;
                default:
                    return baseOptions;
            }
        }
    }

    /**
     * Initialize a new chart with theme-aware settings
     * @param {string} canvasId - ID of the canvas element
     * @param {string} type - Chart type
     * @param {Object} data - Chart data
     * @param {Object} customOptions - Custom chart options to merge
     * @returns {Chart} New Chart.js instance
     */
    createChart(canvasId, type, data, customOptions = {}) {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            return null;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        // Destroy existing chart if one exists
        try {
            const existingChart = Chart.getChart ? Chart.getChart(canvas) : null;
            if (existingChart) {
                existingChart.destroy();
            }
        } catch (e) {
            console.warn('Error checking for existing chart:', e);
            // Fallback for older Chart.js versions
            if (canvas.__chartjs__) {
                canvas.__chartjs__.destroy();
            }
        }

        // Deep clone the data to avoid modifying the original
        const clonedData = JSON.parse(JSON.stringify(data));

        // Set the default colors for the datasets
        if (clonedData.datasets && clonedData.datasets.length > 0) {
            clonedData.datasets.forEach((dataset, index) => {
                // Only set colors if not explicitly defined
                if (!dataset.backgroundColor) {
                    dataset.backgroundColor = type === 'line' ?
                        this.activePalette.datasets[index % this.activePalette.datasets.length] :
                        this.getChartColors(clonedData.labels ? clonedData.labels.length : 6);
                }

                if (!dataset.borderColor && type === 'line') {
                    dataset.borderColor = this.activePalette.borderColors[index % this.activePalette.borderColors.length];
                }
            });

            // Flag that these colors were automatically assigned
            clonedData._userDefinedColors = false;
        }

        // Detect Chart.js version
        const isV3 = Chart.defaults && Chart.defaults.color !== undefined;

        // Get default options based on chart type and version
        const defaultOptions = this.getChartOptions(type);

        // Deep merge default options with custom options
        const options = this.mergeDeep(defaultOptions, customOptions);

        // Create new chart
        try {
            return new Chart(canvas, {
                type: type,
                data: clonedData,
                options: options
            });
        } catch (error) {
            console.error('Error creating chart:', error);
            return null;
        }
    }

    /**
     * Deep merge two objects
     * @param {Object} target - Target object
     * @param {Object} sources - Source objects
     * @returns {Object} Merged object
     */
    mergeDeep(target, ...sources) {
        if (!sources.length) return target;
        const source = sources.shift();

        if (this.isObject(target) && this.isObject(source)) {
            for (const key in source) {
                if (this.isObject(source[key])) {
                    if (!target[key]) Object.assign(target, { [key]: {} });
                    this.mergeDeep(target[key], source[key]);
                } else {
                    Object.assign(target, { [key]: source[key] });
                }
            }
        }

        return this.mergeDeep(target, ...sources);
    }

    /**
     * Check if value is an object
     * @param {*} item - Value to check
     * @returns {boolean} True if object
     */
    isObject(item) {
        return (item && typeof item === 'object' && !Array.isArray(item));
    }
}

// Initialize the theme helper as a global object
document.addEventListener('DOMContentLoaded', () => {
    window.chartThemeHelper = new ChartThemeHelper();
});