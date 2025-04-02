/**
 * Chart.js Theme Helper
 * 
 * This script helps manage Chart.js themes for dark/light mode.
 * It centralizes color management for charts across the application.
 * Compatible with Chart.js v2.x and v3.x
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

        // Set default Chart.js options
        this.setChartDefaults();

        // Get all chart instances
        const chartInstances = this.getAllChartInstances();

        // Update each chart
        chartInstances.forEach(chart => {
            this.updateChartTheme(chart);
        });
    }

    /**
     * Set default options for Chart.js
     */
    setChartDefaults() {
        if (typeof Chart === 'undefined') return;

        try {
            // Handle different Chart.js versions
            if (Chart.defaults) {
                // Chart.js v3.x
                if (Chart.defaults.color !== undefined) {
                    Chart.defaults.color = this.activePalette.text;
                }

                if (Chart.defaults.scale && Chart.defaults.scale.grid) {
                    Chart.defaults.scale.grid.color = this.activePalette.gridLines;
                }

                if (Chart.defaults.scale && Chart.defaults.scale.ticks) {
                    Chart.defaults.scale.ticks.color = this.activePalette.text;
                }

                if (Chart.defaults.plugins && Chart.defaults.plugins.legend) {
                    Chart.defaults.plugins.legend.labels = Chart.defaults.plugins.legend.labels || {};
                    Chart.defaults.plugins.legend.labels.color = this.activePalette.text;
                }

                if (Chart.defaults.plugins && Chart.defaults.plugins.title) {
                    Chart.defaults.plugins.title.color = this.activePalette.text;
                }
            }
            // Chart.js v2.x
            else if (Chart.defaults && Chart.defaults.global) {
                Chart.defaults.global.defaultFontColor = this.activePalette.text;

                if (Chart.defaults.global.elements && Chart.defaults.global.elements.line) {
                    Chart.defaults.global.elements.line.borderColor = this.activePalette.primary;
                }

                if (Chart.defaults.scale && Chart.defaults.scale.gridLines) {
                    Chart.defaults.scale.gridLines.color = this.activePalette.gridLines;
                }
            }
        } catch (error) {
            console.warn('Error setting Chart defaults:', error);
        }
    }

    /**
     * Update a specific chart's theme
     * @param {Chart} chart - The Chart.js instance to update
     */
    updateChartTheme(chart) {
        if (!chart || !chart.options) return;

        try {
            // Chart.js v3.x structure
            if (chart.options.plugins) {
                // Update legend text color
                if (chart.options.plugins.legend) {
                    if (!chart.options.plugins.legend.labels) {
                        chart.options.plugins.legend.labels = {};
                    }
                    chart.options.plugins.legend.labels.color = this.activePalette.text;
                }

                // Update title color
                if (chart.options.plugins.title) {
                    chart.options.plugins.title.color = this.activePalette.text;
                }
            }

            // Chart.js v2.x structure
            if (chart.options.legend) {
                if (!chart.options.legend.labels) {
                    chart.options.legend.labels = {};
                }
                chart.options.legend.labels.fontColor = this.activePalette.text;
            }

            if (chart.options.title) {
                chart.options.title.fontColor = this.activePalette.text;
            }

            // Update scales (works for both v2.x and v3.x with different structures)
            if (chart.options.scales) {
                // v3.x structure
                if (chart.options.scales.x) {
                    if (!chart.options.scales.x.ticks) chart.options.scales.x.ticks = {};
                    if (!chart.options.scales.x.grid) chart.options.scales.x.grid = {};

                    chart.options.scales.x.ticks.color = this.activePalette.text;
                    chart.options.scales.x.grid.color = this.activePalette.gridLines;

                    if (chart.options.scales.x.title) {
                        chart.options.scales.x.title.color = this.activePalette.text;
                    }
                }

                if (chart.options.scales.y) {
                    if (!chart.options.scales.y.ticks) chart.options.scales.y.ticks = {};
                    if (!chart.options.scales.y.grid) chart.options.scales.y.grid = {};

                    chart.options.scales.y.ticks.color = this.activePalette.text;
                    chart.options.scales.y.grid.color = this.activePalette.gridLines;

                    if (chart.options.scales.y.title) {
                        chart.options.scales.y.title.color = this.activePalette.text;
                    }
                }

                // v2.x structure
                if (chart.options.scales.xAxes && Array.isArray(chart.options.scales.xAxes)) {
                    chart.options.scales.xAxes.forEach(axis => {
                        if (!axis.ticks) axis.ticks = {};
                        if (!axis.gridLines) axis.gridLines = {};

                        axis.ticks.fontColor = this.activePalette.text;
                        axis.gridLines.color = this.activePalette.gridLines;
                    });
                }

                if (chart.options.scales.yAxes && Array.isArray(chart.options.scales.yAxes)) {
                    chart.options.scales.yAxes.forEach(axis => {
                        if (!axis.ticks) axis.ticks = {};
                        if (!axis.gridLines) axis.gridLines = {};

                        axis.ticks.fontColor = this.activePalette.text;
                        axis.gridLines.color = this.activePalette.gridLines;
                    });
                }
            }

            // For pie/doughnut charts, update background colors if needed
            if (chart.config && (chart.config.type === 'pie' || chart.config.type === 'doughnut')) {
                if (chart.data && chart.data.datasets && chart.data.datasets[0]) {
                    // Only update if colors weren't explicitly defined by user
                    if (!chart.data._userDefinedColors) {
                        chart.data.datasets[0].backgroundColor = this.activePalette.datasets;
                        chart.data.datasets[0].borderColor = this.activePalette.borderColors;
                    }
                }
            }

            // Update the chart
            if (typeof chart.update === 'function') {
                chart.update();
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

        // Base options structure for v3
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

            // Add type-specific options for v3
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
                                },
                                title: {
                                    display: false,
                                    color: this.activePalette.text
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