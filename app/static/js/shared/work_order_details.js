/**
 * Work Order Details JavaScript
 * 
 * This file handles the interactive functionality for the Work Order Details view.
 */

// Document ready function
$(document).ready(function () {
    // Initialize datatables
    if ($.fn.DataTable) {
        if ($('#commentsTable').length) {
            $('#commentsTable').DataTable({
                order: [[2, 'desc']], // Sort by date, newest first
                language: {
                    search: "Filter:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries",
                    infoEmpty: "Showing 0 to 0 of 0 entries",
                    infoFiltered: "(filtered from _MAX_ total entries)"
                }
            });
        }

        if ($('#laborTable').length) {
            $('#laborTable').DataTable({
                order: [[3, 'desc']], // Sort by date, newest first
                language: {
                    search: "Filter:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries",
                    infoEmpty: "Showing 0 to 0 of 0 entries",
                    infoFiltered: "(filtered from _MAX_ total entries)"
                }
            });
        }
    }
});