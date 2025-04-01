"""
New Customer Accounts Routes.

This module defines the routes for the New Customer Accounts report blueprint.
"""

import logging
from datetime import datetime, timedelta
from flask import render_template, request, jsonify

from app.core.database import execute_query
from app.reports.ssrs.new_customer_accounts import bp
from app.reports.ssrs.new_customer_accounts.queries import (
    get_new_customer_accounts,
    get_account_type_summary,
    get_daily_new_accounts,
    format_date_for_query
)

# Configure logger
logger = logging.getLogger(__name__)


@bp.route('/')
def index():
    """
    Render the main report page.
    
    Returns:
        str: Rendered HTML template.
    """
    try:
        # Default to last 30 days
        default_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        return render_template(
            'ssrs/new_customer_accounts/index.html',
            title='New Customer Accounts Report',
            default_date=default_date
        )
        
    except Exception as e:
        logger.error(f"Error rendering report index: {str(e)}")
        return render_template('error.html', error=str(e))


@bp.route('/data')
def get_report_data():
    """
    Get report data as JSON for AJAX requests.
    
    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get move-in date filter from request
        move_in_date_str = request.args.get('move_in_date', '')
        
        # Parse date if provided
        if move_in_date_str:
            move_in_date = datetime.strptime(move_in_date_str, '%Y-%m-%d')
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        else:
            # Use default date (30 days ago)
            move_in_date = datetime.now() - timedelta(days=30)
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        
        # Get query and parameters
        query, params = get_new_customer_accounts(move_in_date)
        
        # Execute query
        results = execute_query(query, params)
        
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'filters': {
                'move_in_date': move_in_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching report data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/account-types')
def get_account_types():
    """
    Get account type summary data.
    
    Returns:
        Response: JSON response with account type summary.
    """
    try:
        # Get move-in date filter from request
        move_in_date_str = request.args.get('move_in_date', '')
        
        # Parse date if provided
        if move_in_date_str:
            move_in_date = datetime.strptime(move_in_date_str, '%Y-%m-%d')
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        else:
            # Use default date (30 days ago)
            move_in_date = datetime.now() - timedelta(days=30)
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        
        # Get query and parameters
        query, params = get_account_type_summary(move_in_date)
        
        # Execute query
        results = execute_query(query, params)
        
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': results,
            'filters': {
                'move_in_date': move_in_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching account type data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/daily-accounts')
def get_daily_accounts():
    """
    Get daily new accounts data.
    
    Returns:
        Response: JSON response with daily accounts data.
    """
    try:
        # Get move-in date filter from request
        move_in_date_str = request.args.get('move_in_date', '')
        
        # Parse date if provided
        if move_in_date_str:
            move_in_date = datetime.strptime(move_in_date_str, '%Y-%m-%d')
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        else:
            # Use default date (30 days ago)
            move_in_date = datetime.now() - timedelta(days=30)
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        
        # Get query and parameters
        query, params = get_daily_new_accounts(move_in_date)
        
        # Execute query
        results = execute_query(query, params)
        
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': results,
            'filters': {
                'move_in_date': move_in_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching daily accounts data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/export')
def export_report():
    """
    Export report data to CSV.
    
    Returns:
        Response: CSV file download.
    """
    try:
        from flask import Response
        import csv
        from io import StringIO
        
        # Get move-in date filter from request
        move_in_date_str = request.args.get('move_in_date', '')
        
        # Parse date if provided
        if move_in_date_str:
            move_in_date = datetime.strptime(move_in_date_str, '%Y-%m-%d')
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        else:
            # Use default date (30 days ago)
            move_in_date = datetime.now() - timedelta(days=30)
            move_in_date = move_in_date.replace(hour=0, minute=0, second=0)
        
        # Get query and parameters
        query, params = get_new_customer_accounts(move_in_date)
        
        # Execute query
        results = execute_query(query, params)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No data to export'
            }), 404
        
        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header row
        writer.writerow(results[0].keys())
        
        # Write data rows
        for row in results:
            writer.writerow(row.values())
        
        # Create response with CSV file
        output = si.getvalue()
        filename = f"new_customer_accounts_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500