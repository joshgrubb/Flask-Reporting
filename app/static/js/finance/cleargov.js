/**
 * ClearGov Widget Manager
 * 
 * This script handles the loading state of ClearGov embedded widgets,
 * showing and hiding loading indicators appropriately.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize loading state management
    initializeWidgetLoaders();

    // Handle window resize for better responsiveness
    setupResponsiveHandling();
});

/**
 * Initialize loading state management for all ClearGov widgets
 */
function initializeWidgetLoaders() {
    // For each widget, set up an observer to detect when the iframe is added by ClearGov
    const widgets = document.querySelectorAll('[id^="cleargov-widget-"]');

    console.log('Initializing widget loaders for', widgets.length, 'widgets');

    widgets.forEach(widget => {
        // Get widget name from data attribute for consistent naming
        const widgetName = widget.getAttribute('data-widget-name');

        if (!widgetName) {
            console.warn('Widget missing data-widget-name attribute:', widget.id);
            return;
        }

        const loadingId = `loading-${widgetName}`;
        const loadingElement = document.getElementById(loadingId);

        if (!loadingElement) {
            console.warn(`Loading indicator not found for widget: ${widgetName}`);
            return;
        }

        console.log(`Setting up observer for widget: ${widgetName}`);

        // Create observer to watch for iframe additions
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.addedNodes.length) {
                    // Check if an iframe was added
                    const iframes = widget.querySelectorAll('iframe');
                    if (iframes.length > 0) {
                        console.log(`Iframe detected in widget: ${widgetName}`);

                        // Hide loading indicator after short delay to ensure content is visible
                        setTimeout(() => {
                            loadingElement.style.display = 'none';
                            console.log(`Loading indicator hidden for: ${widgetName}`);
                        }, 500);

                        // Disconnect observer once iframe is found
                        observer.disconnect();
                    }
                }
            });
        });

        // Start observing with all necessary options
        observer.observe(widget, {
            childList: true,  // Watch for child changes
            subtree: true,    // Watch descendants too
            attributes: false // Don't need to watch attributes
        });

        // Fallback: Hide loading indicator after 10 seconds regardless
        setTimeout(() => {
            if (loadingElement && loadingElement.style.display !== 'none') {
                loadingElement.style.display = 'none';
                console.log(`Fallback timeout: loading indicator hidden for: ${widgetName}`);
            }
        }, 10);
    });
}

/**
 * Set up responsive handling for widgets
 */
function setupResponsiveHandling() {
    // Handle initial size
    adjustForScreenSize();

    // Set up event listener for window resize
    window.addEventListener('resize', function () {
        adjustForScreenSize();
    });
}

/**
 * Adjust widget containers based on screen size
 */
function adjustForScreenSize() {
    const isMobile = window.innerWidth < 768;
    const containers = document.querySelectorAll('.widget-container');

    containers.forEach(container => {
        // Adjust padding for mobile
        container.style.padding = isMobile ? '0.5rem' : '1rem';
    });

    console.log('Adjusted widgets for', isMobile ? 'mobile' : 'desktop', 'view');
}