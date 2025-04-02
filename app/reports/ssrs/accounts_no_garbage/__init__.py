"""
Accounts No Garbage Report Blueprint.

This module defines the blueprint for the Accounts No Garbage report conversion.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "accounts_no_garbage",
    __name__,
    url_prefix="/accounts_no_garbage",
    template_folder="../../../templates/ssrs/accounts_no_garbage",
)

# Import routes at the bottom to avoid circular imports
from app.reports.ssrs.accounts_no_garbage import routes  # noqa
