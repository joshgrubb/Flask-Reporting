"""
Water No Sewer Report Blueprint.

This module defines the blueprint for the Water No Sewer report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "water_no_sewer",
    __name__,
    url_prefix="/water_no_sewer",
    template_folder="../../../templates/groups/utilities_billing/water_no_sewer",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.water_no_sewer import routes  # noqa
