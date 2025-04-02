"""
No Occupant List for Moveouts Report Blueprint.

This module defines the blueprint for the No Occupant List for Moveouts SSRS report conversion.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "no_occupant_list_for_moveouts",
    __name__,
    url_prefix="/no_occupant_list_for_moveouts",
    template_folder="../../../templates/ssrs/no_occupant_list_for_moveouts",
)

# Import routes at the bottom to avoid circular imports
from app.reports.ssrs.no_occupant_list_for_moveouts import routes  # noqa
