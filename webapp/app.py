"""
Sales Automation AI Web Application
Main application module that initializes and configures the Flask application.
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_replace_in_production'),
        DATABASE=os.path.join(app.instance_path, 'sales_automation.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB max upload
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass
    
    # Apply the ProxyFix middleware if behind a proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints
    from webapp.routes.auth import auth_bp
    from webapp.routes.dashboard import dashboard_bp
    from webapp.routes.inventory import inventory_bp
    from webapp.routes.orders import orders_bp
    from webapp.routes.settings import settings_bp
    from webapp.api.v1 import api_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)

def register_error_handlers(app):
    """Register error handlers."""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html', error=str(e)), 400

def run_app(app=None, host='0.0.0.0', port=8080, debug=False):
    """Run the Flask application."""
    if app is None:
        app = create_app()
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    app = create_app()
    run_app(app, debug=True) 