function filterGroups() {
    var input = document.getElementById("groupSearch").value.toLowerCase();
    var tiles = document.getElementsByClassName("group-tile");
    var noResults = document.getElementById("noResults");
    var visibleCount = 0;

    for (var i = 0; i < tiles.length; i++) {
        let titleText = tiles[i].querySelector('.card-title').innerText.toLowerCase();
        let descText = tiles[i].querySelector('.card-text').innerText.toLowerCase();

        if (titleText.indexOf(input) > -1 || descText.indexOf(input) > -1) {
            tiles[i].style.display = "";
            visibleCount++;
        } else {
            tiles[i].style.display = "none";
        }
    }

    // Show/hide no results message
    noResults.style.display = visibleCount === 0 ? "block" : "none";
}

// Add animation to cards when page loads
document.addEventListener('DOMContentLoaded', function () {
    const tiles = document.getElementsByClassName("group-tile");
    for (let i = 0; i < tiles.length; i++) {
        setTimeout(function () {
            tiles[i].style.opacity = "1";
            tiles[i].style.transform = "translateY(0)";
        }, i * 100);
    }
});
// Handle URL search parameter for the dashboard page
document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');

    if (searchQuery) {
        // Auto-fill the search input
        const groupSearch = document.getElementById('groupSearch');
        if (groupSearch) {
            groupSearch.value = searchQuery;
            // Trigger the filter function
            filterGroups();
        }

        // Show a notification that we're filtering by the search term
        const container = document.querySelector('.container');
        if (container) {
            const notification = document.createElement('div');
            notification.className = 'alert alert-info alert-dismissible fade show mt-3';
            notification.innerHTML = `
                <i class="fas fa-search"></i> Showing results for: <strong>${searchQuery}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            container.insertBefore(notification, container.firstChild);
        }
    }
});  