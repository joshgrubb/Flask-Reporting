# Flask-Reporting
Flask app to replace Power BI reports with Python
flask-reporting-platform/
├── app/
│   ├── __init__.py           # Application factory
│   ├── core/                 # Shared functionality
│   │   ├── __init__.py
│   │   ├── database.py       # Database connections
│   │   ├── auth.py           # Authentication
│   │   └── utils.py          # Shared utilities
│   ├── reports/              # Report modules
│   │   ├── __init__.py
│   │   ├── powerbi/          # Power BI report replacements
│   │   │   ├── __init__.py
│   │   │   ├── report1/      # First Power BI report
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   └── queries.py
│   │   │   ├── report2/
│   │   │   └── ...
│   │   └── ssrs/             # SSRS report replacements
│   │       ├── __init__.py
│   │       ├── report1/
│   │       └── ...
│   ├── static/
│   └── templates/
│       ├── base.html         # Base template
│       ├── dashboard.html    # Main dashboard
│       ├── powerbi/          # Templates for Power BI reports
│       └── ssrs/             # Templates for SSRS reports
├── config.py                 # Configuration
└── run.py                    # Application entry point
