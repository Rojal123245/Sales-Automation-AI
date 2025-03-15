"""
Settings routes for the web application.
Handles user preferences and application settings.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

# Create the blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def index():
    """Render the main settings page."""
    # This is a placeholder - we'll implement actual settings views later
    return render_template('settings/index.html')

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit user profile."""
    # This is a placeholder - we'll implement actual profile editing later
    return render_template('settings/profile.html')

@settings_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Edit user preferences."""
    # This is a placeholder - we'll implement actual preferences editing later
    return render_template('settings/preferences.html') 