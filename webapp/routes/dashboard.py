"""
Dashboard routes for the web application.
Handles the main dashboard views and data.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

# Create the blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Render the main dashboard page."""
    # This is a placeholder - we'll implement actual dashboard later
    return render_template('dashboard/index.html')

@dashboard_bp.route('/data')
@login_required
def dashboard_data():
    """Return JSON data for dashboard visualizations."""
    # This is a placeholder - we'll implement actual data endpoints later
    return jsonify({
        'status': 'success',
        'message': 'Dashboard data endpoint placeholder'
    }) 