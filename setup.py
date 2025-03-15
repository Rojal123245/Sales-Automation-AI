from setuptools import setup, find_packages

setup(
    name="sales-automation-ai",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.2.0",
        "pandas>=1.5.0",
        "numpy>=1.22.0",
        "matplotlib>=3.5.0",
        "scikit-learn>=1.0.0",
        "statsmodels>=0.13.0",
        "werkzeug>=2.2.0",
        "flask-login>=0.6.0",
    ],
    entry_points={
        "console_scripts": [
            "sales-webapp=webapp.app:run_app",
        ],
    },
    python_requires=">=3.8",
    author="Sales Automation Team",
    author_email="info@salesautomation.ai",
    description="AI-powered sales forecasting and inventory automation",
    keywords="sales, ai, forecasting, inventory, automation",
    url="https://github.com/your-organization/sales-automation-ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Business/Industry",
        "Programming Language :: Python :: 3",
    ],
) 