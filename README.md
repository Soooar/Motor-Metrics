# MotorMetrics 🚗📊

*Read this in [Portuguese](README-pt.md).*

## 🎯 Business Objective
The automotive market is highly dynamic, and vehicle depreciation is a key factor in buying and selling decisions. This **Data Engineering and Analytics Engineering** project aims to automatically monitor the real depreciation of used vehicles.

Through an ETL/ELT pipeline, the system cross-references prices from real online listings with official reference values (FIPE Table). The main KPI tracked is the **Depreciation Rate (Market vs. FIPE Spread)**, allowing the identification of business opportunities, regional price distortions, and the depreciation curve behavior by year/model.

## 🛠️ Tech Stack
* **Language:** Python
* **Extraction & Processing:** `requests`, `BeautifulSoup`, `pandas`
* **Storage:** AWS S3 (Data Lake) and PostgreSQL (Data Warehouse)
* **Transformation (Analytics Engineering):** dbt (Data Build Tool)
* **Orchestration & CI/CD:** GitHub Actions
* **Data Visualization (BI):** Power BI

## 🏗️ Project Architecture

> [!NOTE]  
> *(Placeholder)* The pipeline architecture diagram (Miro/Draw.io) will be inserted here illustrating the flow: `Internet -> AWS S3 -> PostgreSQL -> dbt -> Power BI`.

## 🚀 How to Run Locally

### Prerequisites
* Python 3.10+
* PostgreSQL running locally (native or via Docker)
* AWS Account (optional for purely local testing, required for S3 flow)

### Step-by-Step

# 1. Clone the repository and enter the folder
git clone https://github.com/Soooar/Motor-Metrics.git
cd MotorMetrics

# 2. Create and activate the virtual environment (Windows)
python -m venv venv
./venv/Scripts/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Run the initial extraction script
python src/extrator_massa.py

> [!TIP]
> If you are on Linux or macOS, use `source venv/bin/activate` to activate the environment.
