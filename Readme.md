# Sales Automation AI

## Project Overview

Sales Automation AI is a system designed to automate the inventory ordering process for retail stores. By analyzing past sales data, it predicts future demand, ensuring optimal stock levels. The system automatically places orders for items through warehouse systems using automation tools, generates performance reports, and provides insights into inventory management. It also serves as a SaaS product, allowing users to monitor AI performance and customize features.

## Project Structure

```
sales-automation/
├── config/
│   └── config.yaml
├── data/
│   └── retail_store_data.csv
├── models/
│   ├── __init__.py
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── tests/
│   └── test_models.py
├── notebooks/
│   └── exploration.ipynb
├── automation/
│   ├── __init__.py
│   ├── warehouse.py
│   ├── order_manager.py
│   └── visualization.py
├── scripts/
│   └── download_models.py
└── main.py

```

## Getting Started

1. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

2. **Set Up Configuration**:

Edit `config/config.yaml` to customize settings.

3. **Get Model Files**:

The model files are not included in the repository due to size constraints. You have two options:

- **Train the model locally**:

  ```bash
  python main.py --mode train
  ```

- **Download pre-trained models**:
  ```bash
  python scripts/download_models.py
  ```

For more details on model handling, see [README_MODEL_HANDLING.md](README_MODEL_HANDLING.md).

4. **Run the automation**:

```bash
python main.py --mode automate
```

## Roadmap

### Phase 1: Data Collection and Preprocessing

**Objective:** Gather and clean historical sales data.

**Steps:**

1. Collect 3 years of sales data, including item names, sales volume, prices, stock levels, and dates.
2. Preprocess the data: Handle missing values, normalize numerical fields, and create derived features (e.g., moving averages, sell-through rates).
3. Identify key performance metrics such as sales trends, revenue contribution, and stale inventory.

**Deliverables:**

- Cleaned dataset with engineered features.
- Summary statistics and visualizations for exploratory data analysis (EDA).

### Phase 2: Model Development

**Objective:** Build predictive models for sales and inventory management.

**Steps:**

1. Develop regression models (e.g., Linear Regression, ARIMA) for future sales predictions.
2. Use classification models (e.g., Random Forest, Logistic Regression) to label items as "Reorder," "Review," or "No Action."
3. Validate models with metrics such as RMSE, precision, and recall.

**Deliverables:**

- Trained and validated prediction models.
- Code to retrain models periodically with new data.

### Phase 3: Automation System

**Objective:** Automate the ordering process.

**Steps:**

1. Use Selenium or similar tools to interact with warehouse systems and place orders.
2. Implement logic to input item codes/names, quantities, and confirm orders.
3. Set up logging and error handling for automation tasks.

**Deliverables:**

- Automated ordering scripts.
- Configurable settings for warehouse integration.

### Phase 4: Reporting and Insights

**Objective:** Provide actionable insights for users.

**Steps:**

1. Create dashboards showing:
   - Top-performing items.
   - Underperforming items.
   - Suggested reorder quantities.
   - Stock level forecasts.
2. Generate downloadable reports (e.g., PDF, CSV).

**Deliverables:**

- Interactive dashboard and periodic report generation functionality.

### Phase 5: SaaS Product Development

**Objective:** Make the system available as a SaaS product.

**Steps:**

1. Develop a multi-tenant web application with user authentication and access control.
2. Implement an admin panel for configuration and monitoring.
3. Offer subscription plans and billing integrations.

**Deliverables:**

- Deployed SaaS platform.
- Documentation for onboarding users.

### Phase 6: Testing and Deployment

**Objective:** Ensure system reliability and scalability.

**Steps:**

1. Conduct unit, integration, and end-to-end testing.
2. Test automation scripts across different warehouse platforms.
3. Deploy the system on cloud infrastructure (e.g., AWS, GCP, Azure).

**Deliverables:**

- Tested and deployed system.
- Post-deployment monitoring setup.
