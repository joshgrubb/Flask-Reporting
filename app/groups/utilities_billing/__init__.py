"""
Utilities Billing Group Module.

This module defines the blueprint for the Utilities Billing group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "utilities_billing",
    __name__,
    url_prefix="/utilities_billing",
    template_folder="../../templates/groups/utilities_billing",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing import routes  # noqa

# Import and register report blueprints
from app.groups.utilities_billing.accounts_no_garbage import (
    bp as accounts_no_garbage_bp,
)  # noqa

bp.register_blueprint(accounts_no_garbage_bp)

from app.groups.utilities_billing.new_customer_accounts import (
    bp as new_customer_accounts_bp,
)  # noqa

bp.register_blueprint(new_customer_accounts_bp)

from app.groups.utilities_billing.no_occupant_list_for_moveouts import (
    bp as no_occupant_list_bp,
)  # noqa

bp.register_blueprint(no_occupant_list_bp)

from app.groups.utilities_billing.amount_billed_search import (
    bp as amount_billed_search_bp,
)  # noqa

bp.register_blueprint(amount_billed_search_bp)


from app.groups.utilities_billing.trending import (
    bp as trending_bp,
)  # noqa
bp.register_blueprint(trending_bp)

from app.groups.utilities_billing.cash_only_accounts import (
    bp as cash_only_accounts_bp,
)  # noqa

bp.register_blueprint(cash_only_accounts_bp)
