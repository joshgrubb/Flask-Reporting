/**
 * Dynamic navbar search functionality
 * This script dynamically builds report data from the navigation structure
 * and provides search capabilities
 */

// IIFE to avoid polluting global scope
(function () {
    // Execute when DOM is loaded
    document.addEventListener('DOMContentLoaded', function () {
        initNavbarSearch();
    });

    /**
     * Initialize the navbar search functionality
     */
    function initNavbarSearch() {
        const searchForm = document.getElementById('reportSearchForm');
        const searchInput = document.getElementById('navbarSearch');
        const searchButton = document.getElementById('searchButton');

        // Check if search elements exist
        if (!searchForm || !searchInput || !searchButton) {
            console.error('Search elements not found in the DOM');
            return;
        }

        // Build report data from the navigation structure
        const reportData = buildReportDataFromNavigation();

        // Function to perform search
        function performSearch(query) {
            if (!query || query.length < 2) return null;

            query = query.toLowerCase();

            // Find best match - prioritize title matches over group matches
            const titleMatches = reportData.filter(report =>
                report.title.toLowerCase().includes(query)
            );

            if (titleMatches.length > 0) {
                return titleMatches[0]; // Return first title match
            }

            const groupMatches = reportData.filter(report =>
                report.group.toLowerCase().includes(query)
            );

            if (groupMatches.length > 0) {
                return groupMatches[0]; // Return first group match
            }

            return null; // No matches
        }

        // Create and show search results dropdown
        function showSearchResults(query) {
            // Remove any existing dropdown
            const existingDropdown = document.querySelector('.search-results-dropdown');
            if (existingDropdown) {
                existingDropdown.remove();
            }

            if (!query || query.length < 2) return;

            // Filter reports
            query = query.toLowerCase();
            const matchedReports = reportData.filter(report =>
                report.title.toLowerCase().includes(query) ||
                report.group.toLowerCase().includes(query)
            );

            if (matchedReports.length === 0) return;

            // Create dropdown element
            const dropdown = document.createElement('div');
            dropdown.classList.add('dropdown-menu', 'search-results-dropdown');
            dropdown.style.display = 'block';
            dropdown.style.position = 'absolute';
            dropdown.style.width = '100%';
            dropdown.style.top = '100%';
            dropdown.style.left = '0';
            dropdown.style.zIndex = '1000';
            dropdown.style.maxHeight = '300px';
            dropdown.style.overflowY = 'auto';

            // Add results
            matchedReports.slice(0, 8).forEach(report => {
                const item = document.createElement('a');
                item.classList.add('dropdown-item');
                item.href = report.url;

                // Highlight matching text
                const title = document.createElement('div');
                const titleHtml = report.title.replace(
                    new RegExp(query, 'gi'),
                    match => `<span class="bg-primary text-white">${match}</span>`
                );
                title.innerHTML = titleHtml;

                const group = document.createElement('small');
                group.classList.add('text-muted');
                group.textContent = report.group;

                item.appendChild(title);
                item.appendChild(group);
                dropdown.appendChild(item);
            });

            // Add dropdown to the search form
            searchForm.style.position = 'relative';
            searchForm.appendChild(dropdown);
        }

        // Build report data from the navigation structure
        function buildReportDataFromNavigation() {
            const reports = [];

            // Find all dropdown menus
            const dropdowns = document.querySelectorAll('.nav-item.dropdown');

            dropdowns.forEach(dropdown => {
                // Get group name from the dropdown toggle
                const groupToggle = dropdown.querySelector('.dropdown-toggle');
                if (!groupToggle) return;

                const groupName = groupToggle.textContent.trim();
                const groupIcon = groupToggle.querySelector('i')?.className || '';

                // Get reports from dropdown items
                const reportLinks = dropdown.querySelectorAll('.dropdown-item');

                reportLinks.forEach(link => {
                    // Skip the "All X Reports" link
                    if (link.textContent.includes('All') && link.textContent.includes('Reports')) {
                        return;
                    }

                    reports.push({
                        title: link.textContent.trim(),
                        url: link.getAttribute('href'),
                        group: groupName,
                        icon: groupIcon
                    });
                });
            });

            return reports;
        }

        // Handle input changes (debounced)
        let debounceTimer;
        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                showSearchResults(searchInput.value);
            }, 300);
        });

        // Handle form submission
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const matchedReport = performSearch(searchInput.value);

            if (matchedReport) {
                window.location.href = matchedReport.url;
            } else {
                // If no specific report matches, go to the groups page with the search term
                window.location.href = `/groups/?search=${encodeURIComponent(searchInput.value)}`;
            }
        });

        // Handle click outside to close dropdown
        document.addEventListener('click', function (e) {
            if (!searchForm.contains(e.target)) {
                const dropdown = document.querySelector('.search-results-dropdown');
                if (dropdown) {
                    dropdown.remove();
                }
            }
        });
    }
})();