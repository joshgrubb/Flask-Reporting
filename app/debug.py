"""
Debug script to list all registered routes in the Flask application.

Run this script with 'flask shell < debug_routes.py' to see all routes.
"""

import urllib.parse

# Get the current app
from flask import current_app

# Get all registered routes
routes = []
for rule in current_app.url_map.iter_rules():
    routes.append(
        {
            "endpoint": rule.endpoint,
            "methods": ", ".join(rule.methods),
            "url": urllib.parse.unquote(str(rule)),
        }
    )

# Sort routes by URL for easier viewing
routes.sort(key=lambda x: x["url"])

# Print header
print("\n" + "=" * 80)
print("{:<50} {:<20} {:<10}".format("URL", "Endpoint", "Methods"))
print("=" * 80)

# Print routes
for route in routes:
    print(
        "{:<50} {:<20} {:<10}".format(route["url"], route["endpoint"], route["methods"])
    )

print("=" * 80)
print(f"Total routes: {len(routes)}")
print("=" * 80 + "\n")

# Find labor requests routes
labor_routes = [r for r in routes if "labor_requests" in r["url"]]
if labor_routes:
    print("\nLabor Requests Routes:")
    print("-" * 80)
    for route in labor_routes:
        print(
            "{:<50} {:<20} {:<10}".format(
                route["url"], route["endpoint"], route["methods"]
            )
        )
    print("-" * 80)
else:
    print("\nNo Labor Requests routes found!")

# Exit the shell
exit()
