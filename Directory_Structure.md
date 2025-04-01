flask-reporting/
├── app/
│   ├── __init__.py              # Application factory
│   ├── core/                    # Shared functionality
│   │   ├── __init__.py
│   │   ├── database.py          # Database connections
│   │   ├── auth.py              # Authentication
│   │   └── utils.py             # Shared utilities
│   ├── reports/                 # Report modules
│   │   ├── __init__.py          # Reports blueprint registration
│   │   ├── routes.py            # Main reports routes
│   │   ├── powerbi/             # Power BI report replacements
│   │   │   ├── __init__.py
│   │   │   ├── report1/         # Placeholder for future PowerBI report
│   │   │   │   └── __init__.py
│   │   └── ssrs/                # SSRS report replacements
│   │       ├── __init__.py      # SSRS blueprint registration
│   │       ├── routes.py        # SSRS dashboard routes
│   │       └── new_customer_accounts/  # Your first SSRS report
│   │           ├── __init__.py  # Report blueprint
│   │           ├── routes.py    # Report routes
│   │           └── queries.py   # SQL queries
│   ├── static/                  # Static files
│   │   ├── css/
│   │   │   └── style.css        # Custom CSS
│   │   ├── js/
│   │   │   └── main.js          # Custom JavaScript
│   │   └── img/                 # Images folder (create if needed)
│   │       └── loading.gif      # Loading animation (add your own)
│   └── templates/               # HTML templates
│       ├── base.html            # Base template
│       ├── error.html           # Error template
│       ├── reports/             # Reports templates
│       │   └── dashboard.html   # Main reports dashboard
│       └── ssrs/                # SSRS templates
│           ├── dashboard.html   # SSRS dashboard
│           └── new_customer_accounts/  # Templates for your report
│               └── index.html   # Report template
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── test_db_connection.py        # Database connection test
└── test_sample_query.py         # Sample query test
