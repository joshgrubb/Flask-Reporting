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

        // Set default options for Chart.js
        if (Chart.defaults) {
            // Update global defaults if available
            if (Chart.defaults.color !== undefined) {
                Chart.defaults.color = textColor;
            }

            // Update scale defaults if available
            if (Chart.defaults.scale && Chart.defaults.scale.grid) {
                Chart.defaults.scale.grid.color = gridColor;
            }
        }

        // Get all chart instances safely
        // In Chart.js v3+, Chart.instances is a Map, not an array
        try {
            // For Chart.js v3+
            if (Chart.instances) {
                // Convert Map to Array if needed
                const chartInstances = Chart.instances instanceof Map ?
                    Array.from(Chart.instances.values()) :
                    Object.values(Chart.instances);

                chartInstances.forEach(chart => {
                    if (chart && chart.options) {
                        // Update chart options
                        if (chart.options.plugins && chart.options.plugins.legend) {
                            chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
                            chart.options.plugins.legend.labels.color = textColor;
                        }

                        // Update scales if they exist
                        if (chart.options.scales) {
                            if (chart.options.scales.x) {
                                chart.options.scales.x.ticks = chart.options.scales.x.ticks || {};
                                chart.options.scales.x.grid = chart.options.scales.x.grid || {};
                                chart.options.scales.x.ticks.color = textColor;
                                chart.options.scales.x.grid.color = gridColor;
                            }

                            if (chart.options.scales.y) {
                                chart.options.scales.y.ticks = chart.options.scales.y.ticks || {};
                                chart.options.scales.y.grid = chart.options.scales.y.grid || {};
                                chart.options.scales.y.ticks.color = textColor;
                                chart.options.scales.y.grid.color = gridColor;
                            }
                        }

                        // Update the chart
                        chart.update();
                    }
                });
            }
        } catch (error) {
            console.warn('Error updating chart theme:', error);
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