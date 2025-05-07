/**
 * Work Order Details JavaScript
 * 
 * This file handles the interactive functionality for the Work Order Details view.
 */

// Document ready function
$(document).ready(function () {
    // Initialize quick search form
    $('#quickSearchForm').on('submit', function (e) {
        e.preventDefault();
        const workOrderId = $('#quickWorkOrderId').val().trim();

        if (workOrderId) {
            // Get current group from URL path
            const pathParts = window.location.pathname.split('/');
            const groupsIndex = pathParts.indexOf('groups');
            let currentGroup = 'default';

            if (groupsIndex !== -1 && pathParts.length > groupsIndex + 1) {
                currentGroup = pathParts[groupsIndex + 1];
            }

            // Redirect to the work order details page
            window.location.href = `/groups/${currentGroup}/work_orders/${workOrderId}`;
        } else {
            // Show error message
            alert('Please enter a work order ID');
        }
    });

    // Initialize datatables
    if ($.fn.DataTable) {
        // Comments table initialization
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

        // Labor table initialization
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

        // Materials table initialization
        if ($('#materialsTable').length) {
            $('#materialsTable').DataTable({
                order: [[6, 'desc']], // Sort by date column, newest first
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