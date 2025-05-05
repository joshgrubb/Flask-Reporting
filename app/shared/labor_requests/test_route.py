"""
Test module for Labor Requests routes.

This is a temporary module to test that the labor requests routes are working correctly.
"""

from flask import Blueprint, render_template

# Create a test blueprint
test_bp = Blueprint(
    "labor_requests_test",
    __name__,
    url_prefix="/test/labor_requests",
)


@test_bp.route("/")
def test_index():
    """
    Test route to render the labor requests template.

    Returns:
        str: Rendered HTML template.
    """
    return render_template(
        "shared/labor_requests/index.html",
        title="Labor Requests Test",
        categories=[],
        default_start_date="2025-04-05",
        default_end_date="2025-05-05",
        current_group="test",
    )
