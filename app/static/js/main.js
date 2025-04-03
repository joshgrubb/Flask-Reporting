/**
 * Main JavaScript file for Flask Reporting Application
 */

// Show current year in footer
document.addEventListener('DOMContentLoaded', function () {
    // Find elements with the data-current-year attribute
    const yearElements = document.querySelectorAll('[data-current-year]');
    const currentYear = new Date().getFullYear();

    // Update each element with the current year
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );

        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize dark mode
    const darkModeManager = new DarkModeManager();
    window.darkModeManager = darkModeManager;

    // Handle page loader
    setTimeout(function () {
        const pageLoader = document.getElementById('page-loader');
        if (pageLoader) {
            pageLoader.classList.add('loaded');
            setTimeout(() => {
                pageLoader.style.display = 'none';
            }, 300);
        }
    }, 300);

    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        // Scroll to top when button is clicked
        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

/**
 * Dark Mode Manager
 * 
 * Enhanced dark mode functionality for Flask Reporting Application
 * Handles smooth transitions, icon changes, and persists user preference
 */
class DarkModeManager {
    constructor() {
        this.darkModeToggle = document.getElementById('toggle-theme');
        this.htmlElement = document.documentElement;
        this.localStorageKey = 'theme';
        this.isDarkMode = false;

        // Initialize theme from saved preference
        this.initializeTheme();

        // Add event listener for toggle button
        if (this.darkModeToggle) {
            this.darkModeToggle.addEventListener('click', this.toggleDarkMode.bind(this));
        }

        // Listen for system preference changes
        this.setupMediaQueryListener();
    }

    /**
     * Initialize theme based on local storage or system preference
     */
    initializeTheme() {
        // Get saved preference
        const savedTheme = localStorage.getItem(this.localStorageKey);

        if (savedTheme === 'dark') {
            this.enableDarkMode();
        } else if (savedTheme === 'light') {
            this.enableLightMode();
        } else {
            // No saved preference, check system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.enableDarkMode();
            } else {
                this.enableLightMode();
            }
        }
    }

    /**
     * Enable dark mode
     */
    enableDarkMode() {
        this.htmlElement.classList.add('dark-mode');
        localStorage.setItem(this.localStorageKey, 'dark');
        this.isDarkMode = true;
        this.updateToggleIcon();

        // Update charts if they exist
        this.updateChartsTheme(true);
    }

    /**
     * Enable light mode
     */
    enableLightMode() {
        this.htmlElement.classList.remove('dark-mode');
        localStorage.setItem(this.localStorageKey, 'light');
        this.isDarkMode = false;
        this.updateToggleIcon();

        // Update charts if they exist
        this.updateChartsTheme(false);
    }

    /**
     * Toggle between dark and light mode
     * @param {Event} e - Click event
     */
    toggleDarkMode(e) {
        e.preventDefault();

        if (this.isDarkMode) {
            this.enableLightMode();
        } else {
            this.enableDarkMode();
        }
    }

    /**
     * Update the toggle button icon based on current mode
     */
    updateToggleIcon() {
        if (!this.darkModeToggle) return;

        const iconElement = this.darkModeToggle.querySelector('i');
        if (!iconElement) return;

        if (this.isDarkMode) {
            iconElement.classList.remove('fa-moon');
            iconElement.classList.add('fa-sun');
            this.darkModeToggle.setAttribute('data-bs-original-title', 'Switch to light mode');
        } else {
            iconElement.classList.remove('fa-sun');
            iconElement.classList.add('fa-moon');
            this.darkModeToggle.setAttribute('data-bs-original-title', 'Switch to dark mode');
        }

        // Update tooltip if Bootstrap is loaded
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltip = bootstrap.Tooltip.getInstance(this.darkModeToggle);
            if (tooltip) {
                tooltip.dispose();
                new bootstrap.Tooltip(this.darkModeToggle);
            }
        }
    }

    /**
     * Set up listener for system preference changes
     */
    setupMediaQueryListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Add listener for changes if supported
            if (typeof mediaQuery.addEventListener === 'function') {
                mediaQuery.addEventListener('change', e => {
                    if (e.matches) {
                        this.enableDarkMode();
                    } else {
                        this.enableLightMode();
                    }
                });
            }
        }
    }

    /**
     * Update Chart.js theme if charts exist on the page
     * @param {boolean} isDark - Whether dark mode is enabled
     */
    updateChartsTheme(isDark) {
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') return;

        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const textColor = isDark ? '#cbd5e1' : '#5c5f73';

        try {
            // FIX: Instead of modifying global Chart defaults (which can cause recursion),
            // only set them when initializing new charts.
            // Just update existing chart instances directly

            // Get all chart instances safely
            const chartInstances = this.getAllChartInstances();

            // Update each chart
            chartInstances.forEach(chart => {
                // Try-catch around each chart update to prevent errors from stopping other updates
                try {
                    this.updateChartInstance(chart, textColor, gridColor);
                } catch (err) {
                    console.warn('Error updating individual chart:', err);
                }
            });
        } catch (error) {
            console.warn('Error updating chart theme:', error);
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

            // Fallback for Chart.js v4
            if (typeof Chart.getChart === 'function') {
                const canvases = document.querySelectorAll('canvas');
                const charts = [];

                canvases.forEach(canvas => {
                    try {
                        const chart = Chart.getChart(canvas);
                        if (chart) {
                            charts.push(chart);
                        }
                    } catch (e) {
                        // Ignore errors for canvases without charts
                    }
                });

                return charts;
            }

            // No instances found or unsupported version
            return [];
        } catch (error) {
            console.warn('Error getting Chart instances:', error);
            return [];
        }
    }

    /**
     * Update a single chart instance with new theme options
     * @param {Chart} chart - The Chart.js instance to update
     * @param {string} textColor - The text color to use
     * @param {string} gridColor - The grid color to use
     */
    updateChartInstance(chart, textColor, gridColor) {
        if (!chart || !chart.options) return;

        // Use a deep copy approach to avoid potential recursion issues
        const newOptions = JSON.parse(JSON.stringify(chart.options));
        let needsUpdate = false;

        // Safely update options
        if (newOptions.plugins) {
            // Update legend text color
            if (newOptions.plugins.legend && newOptions.plugins.legend.labels) {
                newOptions.plugins.legend.labels.color = textColor;
                needsUpdate = true;
            }

            // Update title color
            if (newOptions.plugins.title) {
                newOptions.plugins.title.color = textColor;
                needsUpdate = true;
            }
        }

        // Update scales for Chart.js v3+
        if (newOptions.scales) {
            if (newOptions.scales.x) {
                if (newOptions.scales.x.ticks) {
                    newOptions.scales.x.ticks.color = textColor;
                    needsUpdate = true;
                }
                if (newOptions.scales.x.grid) {
                    newOptions.scales.x.grid.color = gridColor;
                    needsUpdate = true;
                }
                if (newOptions.scales.x.title) {
                    newOptions.scales.x.title.color = textColor;
                    needsUpdate = true;
                }
            }

            if (newOptions.scales.y) {
                if (newOptions.scales.y.ticks) {
                    newOptions.scales.y.ticks.color = textColor;
                    needsUpdate = true;
                }
                if (newOptions.scales.y.grid) {
                    newOptions.scales.y.grid.color = gridColor;
                    needsUpdate = true;
                }
                if (newOptions.scales.y.title) {
                    newOptions.scales.y.title.color = textColor;
                    needsUpdate = true;
                }
            }

            // Update scales for Chart.js v2.x
            if (Array.isArray(newOptions.scales.xAxes)) {
                newOptions.scales.xAxes.forEach(axis => {
                    if (axis.ticks) {
                        axis.ticks.fontColor = textColor;
                        needsUpdate = true;
                    }
                    if (axis.gridLines) {
                        axis.gridLines.color = gridColor;
                        needsUpdate = true;
                    }
                });
            }

            if (Array.isArray(newOptions.scales.yAxes)) {
                newOptions.scales.yAxes.forEach(axis => {
                    if (axis.ticks) {
                        axis.ticks.fontColor = textColor;
                        needsUpdate = true;
                    }
                    if (axis.gridLines) {
                        axis.gridLines.color = gridColor;
                        needsUpdate = true;
                    }
                });
            }
        }

        // Only update the chart if needed and avoid modifying chart.options directly
        if (needsUpdate && typeof chart.update === 'function') {
            // Use options override instead of modifying the chart directly
            chart.update({
                options: newOptions
            });
        }
    }
}

/**
 * Format a date for display
 * @param {string|Date} dateValue - The date to format
 * @returns {string} - Formatted date string
 */
function formatDate(dateValue) {
    if (!dateValue) return '';

    try {
        const date = new Date(dateValue);
        if (isNaN(date.getTime())) return '';
        return date.toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
}

/**
 * Format a number as currency
 * @param {number} value - The number to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(value) {
    if (value == null) return '';

    try {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return value;

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(numValue);
    } catch (error) {
        console.error('Error formatting currency:', error);
        return value;
    }
}

/**
 * Show an alert message that automatically disappears
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showAlert(message, type = 'info', duration = 3000) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');

    // Add alert content
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Find alert container
    const alertContainer = document.getElementById('alert-container');
    const container = alertContainer || document.querySelector('.container');

    if (container) {
        // Add to container
        container.insertBefore(alertDiv, container.firstChild);

        // Set timeout to remove
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 150);
        }, duration);
    }
}
/**
 * Enhanced DataTables Dark Mode Fixer
 * 
 * This script specifically targets DataTables elements with more aggressive approach
 * to force style changes in both light and dark modes.
 */

class EnhancedDataTablesDarkModeFixer {
    constructor() {
        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });
    }

    init() {
        // Add a small delay to ensure DataTables are initialized
        setTimeout(() => {
            this.applyStyles();

            // Set up continuous checking for the first minute (to handle delayed loading)
            let checkCount = 0;
            const checkInterval = setInterval(() => {
                this.applyStyles();
                checkCount++;
                if (checkCount >= 6) { // Check for 1 minute (6 x 10 seconds)
                    clearInterval(checkInterval);
                }
            }, 10000); // Check every 10 seconds
        }, 500);

        // Set up listeners for theme changes
        this.setupListeners();
    }

    setupListeners() {
        // Listen for theme toggle clicks
        const themeToggle = document.getElementById('toggle-theme');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                // Apply styles immediately and then again after a delay
                setTimeout(() => this.applyStyles(), 50);
                setTimeout(() => this.applyStyles(), 200);
                setTimeout(() => this.applyStyles(), 500);
            });
        }

        // Watch for class changes on HTML element
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        // Apply styles immediately and then again after a delay
                        this.applyStyles();
                        setTimeout(() => this.applyStyles(), 200);
                    }
                });
            });

            observer.observe(document.documentElement, { attributes: true });
        }

        // Handle AJAX completions which might refresh tables
        if (typeof $ !== 'undefined' && $.fn && $.fn.dataTable) {
            $(document).ajaxComplete(() => {
                setTimeout(() => this.applyStyles(), 200);
            });
        }
    }

    applyStyles() {
        const isDarkMode = document.documentElement.classList.contains('dark-mode');

        // Define colors based on the current mode
        const colors = {
            background: isDarkMode ? '#1f2937' : '#ffffff',
            text: isDarkMode ? '#f9fafb' : '#1f2937',
            headerBg: isDarkMode ? '#2d3748' : '#f1f5f9',
            headerText: isDarkMode ? '#e5e7eb' : '#1f2937',
            stripeBg: isDarkMode ? '#111827' : '#edf2f7', // Darker in dark mode, lighter blue-gray in light mode
            hoverBg: isDarkMode ? '#3b4c69' : '#e3e8f0',  // Enhanced hover contrast
            border: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        };

        // Get all DataTables
        this.forceStyleDataTables(colors);
    }

    forceStyleDataTables(colors) {
        // Target all potential DataTables
        const tables = document.querySelectorAll('.dataTable, table.display, table.cell-border, table.stripe, table.hover, table.order-column');
        if (tables.length === 0) return;

        tables.forEach(table => {
            // Force styles using !important
            this.addStyleTag(`
                #${table.id} {
                    background-color: ${colors.background} !important;
                    color: ${colors.text} !important;
                }
                
                #${table.id} thead th, 
                #${table.id} thead td {
                    background-color: ${colors.headerBg} !important;
                    color: ${colors.headerText} !important;
                    border-color: ${colors.border} !important;
                }
                
                #${table.id} tbody tr {
                    background-color: ${colors.background} !important;
                    color: ${colors.text} !important;
                }
                
                #${table.id} tbody tr.odd {
                    background-color: ${colors.stripeBg} !important;
                }
                
                #${table.id} tbody tr:hover {
                    background-color: ${colors.hoverBg} !important;
                }
                
                #${table.id} tbody td {
                    background-color: transparent !important;
                    color: ${colors.text} !important;
                    border-color: ${colors.border} !important;
                }
                
                .dataTables_wrapper .dataTables_length, 
                .dataTables_wrapper .dataTables_filter, 
                .dataTables_wrapper .dataTables_info, 
                .dataTables_wrapper .dataTables_processing, 
                .dataTables_wrapper .dataTables_paginate {
                    color: ${colors.text} !important;
                }
                
                .dataTables_wrapper .dataTables_filter input,
                .dataTables_wrapper .dataTables_length select {
                    background-color: ${colors.background} !important;
                    color: ${colors.text} !important;
                    border: 1px solid ${colors.border} !important;
                }
            `);

            // Also apply direct styles to the elements
            try {
                // Style table
                table.style.setProperty('background-color', colors.background, 'important');
                table.style.setProperty('color', colors.text, 'important');

                // Style headers
                const headers = table.querySelectorAll('thead th, thead td');
                headers.forEach(header => {
                    header.style.setProperty('background-color', colors.headerBg, 'important');
                    header.style.setProperty('color', colors.headerText, 'important');
                });

                // Style all rows directly
                const allRows = table.querySelectorAll('tbody tr');
                allRows.forEach(row => {
                    // Base styling for all rows
                    row.style.setProperty('background-color', colors.background, 'important');
                    row.style.setProperty('color', colors.text, 'important');

                    // Special styling for odd rows
                    if (row.classList.contains('odd')) {
                        row.style.setProperty('background-color', colors.stripeBg, 'important');
                    }

                    // Style all cells in the row
                    const cells = row.querySelectorAll('td');
                    cells.forEach(cell => {
                        cell.style.setProperty('background-color', 'transparent', 'important');
                        cell.style.setProperty('color', colors.text, 'important');
                    });
                });
            } catch (error) {
                console.error('Error applying styles directly:', error);
            }
        });
    }

    addStyleTag(css) {
        // Create an ID based on the CSS content to avoid duplicates
        const hash = this.hashString(css);
        const id = `datatable-fix-${hash}`;

        // Check if style already exists
        if (!document.getElementById(id)) {
            const style = document.createElement('style');
            style.id = id;
            style.type = 'text/css';
            style.innerHTML = css;
            document.head.appendChild(style);
        }
    }

    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash).toString(16).substring(0, 8);
    }
}

// Initialize the enhanced fixer
const enhancedDataTablesFixer = new EnhancedDataTablesDarkModeFixer();

// Handle any DataTables that might be initialized after this script runs
if (typeof $ !== 'undefined') {
    $(document).on('init.dt', function () {
        setTimeout(() => {
            if (enhancedDataTablesFixer) {
                enhancedDataTablesFixer.applyStyles();
            }
        }, 100);
    });
}