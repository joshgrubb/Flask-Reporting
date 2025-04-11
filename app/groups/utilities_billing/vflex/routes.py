# app/groups/utilities_billing/vflex/routes.py
"""
VFLEX Routes.

This module defines the routes for the VFLEX report blueprint.
"""

import logging
import csv
import os
from datetime import datetime
from io import StringIO

from flask import render_template, request, jsonify, Response, current_app, send_file

from app.core.database import execute_query
from app.groups.utilities_billing.vflex import bp
from app.groups.utilities_billing.vflex.queries import (
    get_vflex_data,
    get_vflex_error_log,
    get_execution_stats,
    get_vflex_record_count,
)

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the main report page.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # Get statistics for dashboard
        query, params, db_key = get_execution_stats()
        stats = execute_query(query, params, db_key=db_key, fetch_all=False)

        # Get record count estimate
        try:
            count_query, count_params, count_db_key = get_vflex_record_count()
            record_count = execute_query(
                count_query, count_params, db_key=count_db_key, fetch_all=False
            )
            count = record_count.get("RecordCount", "Unknown")
        except Exception as count_error:
            logger.error("Error getting record count: %s", str(count_error))
            count = "Error calculating"

        return render_template(
            "groups/utilities_billing/vflex/index.html",
            title="VFLEX for Sensus",
            stats=stats,
            record_count=count,
        )

    except Exception as e:
        logger.error("Error rendering VFLEX report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get VFLEX data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get pagination parameters
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("limit", 50))

        # Execute the stored procedure query
        query, params, db_key = get_vflex_data()
        all_results = execute_query(query, params, db_key=db_key)

        # Calculate total pages and paginate results
        total_results = len(all_results)
        total_pages = (total_results + page_size - 1) // page_size

        # Calculate start and end indices for pagination
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_results)

        # Get paginated results
        paginated_results = all_results[start_idx:end_idx]

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": paginated_results,
                "total": total_results,
                "page": page,
                "pages": total_pages,
            }
        )

    except Exception as e:
        logger.error("Error fetching VFLEX data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/logs")
def get_logs():
    """
    Get error logs for the VFLEX process.

    Returns:
        Response: JSON response with log data.
    """
    try:
        # Get limit parameter
        limit = int(request.args.get("limit", 100))

        # Execute query
        query, params, db_key = get_vflex_error_log(limit)
        results = execute_query(query, params, db_key=db_key)

        # Format timestamps for JSON serialization
        for row in results:
            if row.get("ErrorTime"):
                row["ErrorTime"] = (
                    row["ErrorTime"].isoformat()
                    if hasattr(row["ErrorTime"], "isoformat")
                    else row["ErrorTime"]
                )

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error("Error fetching VFLEX logs: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_data():
    """
    Export the VFLEX data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Execute the stored procedure query
        query, params, db_key = get_vflex_data()
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        header_row = list(results[0].keys())
        writer.writerow(header_row)

        # Write data rows
        for row in results:
            writer.writerow([row.get(column, "") for column in header_row])

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"VFLEX_Export_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting VFLEX data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export-fixed")
def export_fixed_width():
    """
    Export the VFLEX data to a fixed-width text file format.
    This format is required for importing into the Sensus system.

    Returns:
        Response: Text file download.
    """
    try:
        # Execute the stored procedure query
        query, params, db_key = get_vflex_data()
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Specs for fixed-width file format fields (field name, width)
        field_specs = [
            ("MeterID", 20),
            ("SecondaryMeterID", 20),
            ("RadioID", 12),
            ("Manufacturer", 15),
            ("DeviceStatus", 3),
            ("Commodity", 1),
            ("PhysicalLocationIdentifier", 30),
            ("ServiceDeliveryPointState", 2),
            ("Latitude", 20),  # Ensure enough space for decimal values
            ("Longitude", 20),  # Ensure enough space for decimal values
            ("StreetAddress", 50),
            ("City", 30),
            ("State", 2),
            ("ZipCode", 10),
            ("AccountID", 30),
            ("AccountStatus", 10),
            ("AccountServiceType", 20),
            ("BillingCycle", 5),
            ("RateCode", 10),
            ("RouteID", 10),
            ("ExportUnitOfMeasure", 5),
            ("BillingSystemAndCISMeterMultiplier", 10),
            ("DisplayMultiplier", 10),
            ("BillingSystemandCISMeterMultiplierandDisplayMultiplier", 10),
            ("DateOfLastBill", 10),
            ("UnbilledMeterStatus", 5),
            ("FlowIDentifier", 20),
            ("ZoneIdentifier", 20),
            ("MeterSize", 15),
            ("NumberOfDials", 5),
            ("LastReading", 15),
            ("LowLimitThreshold", 15),
            ("HighLimitThreshold", 15),
            ("CustomerName", 50),
            ("PhoneNumber", 15),
            ("CellPhoneNumber", 15),
            ("CustomerEmail", 50),
            ("SecurityTokenForAccountSetup", 20),
            ("PortalTierLabel", 20),
            ("PortalTierValue", 20),
            ("PortalTierMultiplier", 10),
            ("CustomerPortalEnabled", 1),
            ("CTMultiplier", 10),
            ("MeterBase", 15),
            ("MeterClass", 15),
            ("MeterForm", 15),
            ("Phase", 10),
            ("FeederID", 20),
            ("SubstationID", 20),
            ("SubstationLatitude", 20),
            ("SubstationLongitude", 20),
            ("TransformerID", 20),
            ("TransformerLatitude", 20),
            ("TransformerLongitude", 20),
            ("TransformerPhase", 10),
            ("TransformerPowerRating", 15),
            ("MeterReadMethod", 10),
            ("AutoReadMeterType", 5),
            ("AutoReadMXUType", 5),
        ]

        # Create output file in memory
        output_lines = []

        # Add header row (only in debug mode)
        if current_app.debug:
            header_line = ""
            for field_name, field_width in field_specs:
                header_line += field_name.ljust(field_width)
            output_lines.append(header_line)

        # Add data rows
        for row in results:
            data_line = ""
            for field_name, field_width in field_specs:
                # Convert None values to empty strings
                value = (
                    str(row.get(field_name, ""))
                    if row.get(field_name) is not None
                    else ""
                )

                # Handle special formatting for numeric fields
                if field_name in [
                    "Latitude",
                    "Longitude",
                    "BillingSystemAndCISMeterMultiplier",
                    "LastReading",
                    "LowLimitThreshold",
                    "HighLimitThreshold",
                ]:
                    if value and value != "None":
                        try:
                            # Format numbers with specific precision
                            if field_name in ["Latitude", "Longitude"]:
                                value = f"{float(value):.6f}"
                            else:
                                value = f"{float(value):.2f}"
                        except ValueError:
                            pass  # Keep as string if conversion fails

                # Format field to specified width
                data_line += value.ljust(field_width)[:field_width]

            output_lines.append(data_line)

        # Create response with fixed-width file
        output = "\n".join(output_lines)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"VFLEX_Export_{timestamp}.txt"

        return Response(
            output,
            mimetype="text/plain",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting VFLEX fixed-width data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
