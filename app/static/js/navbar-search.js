// app/static/js/navbar-search.js (replace with this)
/**
 * Navbar Search functionality
 * 
 * This script handles the search functionality in the navigation bar.
 * It uses the centralized report registry accessible via API.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Get report data from the central registry via API
    fetch('/api/reports')
        .then(response => response.json())
        .then(data => {
            // Store report data for searching
            window.allReports = data.reports || [];
            setupSearch();
        })
        .catch(error => {
            console.error('Error fetching report data:', error);
            // Fallback to searching without data
            setupSearch();
        });

    function setupSearch() {
        const searchForm = document.getElementById('reportSearchForm');
        const searchInput = document.getElementById('navbarSearch');

        if (!searchForm || !searchInput) return;

        searchForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const query = searchInput.value.trim().toLowerCase();
            if (query.length < 2) return;  // Require at least 2 characters

            if (window.allReports && window.allReports.length > 0) {
                // Search through available reports
                const results = searchReports(query);

                if (results.length === 1) {
                    // Single match - navigate directly
                    window.location.href = results[0].url;
                } else if (results.length > 1) {
                    // Multiple matches - show results modal
                    showSearchResults(results, query);
                } else {
                    // No matches - show message
                    showNoResultsMessage(query);
                }
            } else {
                // Fallback if no report data is available
                alert('Search functionality unavailable. Please try again later.');
            }
        });
    }

    function searchReports(query) {
        if (!window.allReports) return [];

        return window.allReports.filter(report => {
            // Search in name, description, and ID
            return (
                (report.name && report.name.toLowerCase().includes(query)) ||
                (report.description && report.description.toLowerCase().includes(query)) ||
                (report.id && report.id.toLowerCase().includes(query))
            );
        });
    }

    function showSearchResults(results, query) {
        // Create or get the search results modal
        let modal = document.getElementById('searchResultsModal');

        if (!modal) {
            // Create modal if it doesn't exist
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'searchResultsModal';
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-labelledby', 'searchResultsModalLabel');
            modal.setAttribute('aria-hidden', 'true');

            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="searchResultsModalLabel">Search Results</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div id="searchResultsList"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
        }

        // Populate results
        const resultsList = document.getElementById('searchResultsList');
        resultsList.innerHTML = '';

        // Add heading
        const heading = document.createElement('h6');
        heading.textContent = `Found ${results.length} results for "${query}"`;
        resultsList.appendChild(heading);

        // Add results
        results.forEach(report => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item p-2 my-2 border-bottom';

            resultItem.innerHTML = `
                <a href="${report.url}" class="d-flex text-decoration-none">
                    <div class="me-3">
                        <i class="${report.icon || 'fas fa-file-alt'} fa-2x text-primary"></i>
                    </div>
                    <div>
                        <h6 class="mb-1">${report.name}</h6>
                        <p class="text-muted small mb-0">
                            ${report.description || ''}
                            <span class="badge bg-secondary ms-2">${report.group_id.replace('_', ' ')}</span>
                        </p>
                    </div>
                </a>
            `;

            resultsList.appendChild(resultItem);
        });

        // Show the modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    function showNoResultsMessage(query) {
        // Create or get the search results modal
        let modal = document.getElementById('searchResultsModal');

        if (!modal) {
            // Create modal if it doesn't exist (same as above)
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'searchResultsModal';
            // ... rest of modal creation
            document.body.appendChild(modal);
        }

        // Show no results message
        const resultsList = document.getElementById('searchResultsList');
        resultsList.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No results found</h5>
                <p class="text-muted">No reports found matching "${query}"</p>
            </div>
        `;

        // Show the modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
});