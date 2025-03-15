"""
API version 1 initialization module.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import routes to register them with the blueprint
from . import auth, inventory, orders, dashboard

# Set up docs for the API
@api_bp.route('/')
def index():
    """API documentation endpoint."""
    return {
        'name': 'Sales Automation AI API',
        'version': '1.0.0',
        'description': 'API for Sales Automation AI platform',
        'endpoints': [
            {'path': '/auth', 'description': 'Authentication endpoints'},
            {'path': '/inventory', 'description': 'Inventory management endpoints'},
            {'path': '/orders', 'description': 'Order management endpoints'},
            {'path': '/dashboard', 'description': 'Dashboard data endpoints'}
        ]
    } 