"""Core application routes."""

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Render main dashboard page."""
    # Example report structure - you'll expand this
    reports = {
        "powerbi": [
            {"id": "sales", "name": "Sales Dashboard"},
            {"id": "inventory", "name": "Inventory Analysis"},
            # Add more reports as you implement them
        ],
        "ssrs": [
            {"id": "finance", "name": "Financial Reports"},
            {"id": "operations", "name": "Operations Summary"},
            # Add more reports as you implement them
        ],
    }
    return render_template("index.html", reports=reports)
