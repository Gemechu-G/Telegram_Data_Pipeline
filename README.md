# Telegram_Data_Pipeline
# Telegram Data Pipeline: Ethiopian Medical Businesses

An end-to-end data pipeline for analyzing public Telegram channel data related to Ethiopian medical businesses. This project leverages dbt for transformations, Dagster for orchestration, and YOLOv8 for data enrichment.

## Project Overview
This project aims to provide insights into medical products, pricing, visual content, and posting trends from Telegram channels.
## Features

* **Data Scraping:** Extracts messages and images from specified public Telegram channels using Telethon.
* **Data Lake:** Stores raw, un-altered Telegram messages (JSON) and images in a structured local file system (mounted Docker volume).
* **Data Warehousing:** Loads raw JSON data into a PostgreSQL database and transforms it using dbt into a star schema (dimensions and facts) for analytical querying.
* **Data Quality:** Implements data quality checks on the dbt models.
* **Object Detection (Coming Soon):** Uses YOLOv8 for detecting objects within scraped images.
* **Feature Engineering (Coming Soon):** Extracts meaningful features from text and image data.
* **API Exposure (Coming Soon):** Provides a FastAPI interface for accessing analytical insights.
* **Orchestration (Coming Soon):** Manages and schedules pipeline tasks using Dagster.

## Setup Instructions
telegram_data_pipeline/
├── .env                    # Environment variables (secrets) - IGNORED BY GIT
├── .gitignore              # Specifies files/folders to ignore from Git
├── Dockerfile              # Docker image definition for your Python application
├── docker-compose.yml      # Orchestrates Docker containers (Postgres, App)
├── README.md               # Project overview and setup instructions (this file)
├── requirements.txt        # Python dependencies list

├── data/                   # Mounted volume for raw and processed data
│   ├── raw/                # Raw, unaltered data ingested from Telegram (JSON, images)
│   │   ├── telegram_messages/ # Raw JSON messages, partitioned by date/channel
│   │   └── telegram_images/   # Raw images, similarly partitioned
│   └── processed/          # (Optional, for intermediate files or small datasets)

├── scripts/                # General utility scripts for pipeline steps
│   ├── scrape_telegram.py      # Task 1: Telegram data scraping
│   └── load_raw_to_db.py       # Task 2: Loading raw data to Postgres

├── dbt_project/            # Your dbt (Data Build Tool) project for transformations
│   ├── models/             # SQL models for your data warehouse
│   │   ├── staging/        # Cleaned and lightly transformed raw data
│   │   └── marts/          # Final analytical tables (star schema)
│   ├── tests/              # Custom dbt tests
│   ├── dbt_project.yml     # dbt project configuration
│   └── profiles.yml        # dbt database connection profiles (linked to env vars)

├── api/                    # FastAPI application for exposing analytical insights (Placeholder)
│   └── ...

├── dagster_pipeline/       # Dagster orchestration definitions (Placeholder)
│   └── ...

├── .vscode/                # (Optional) VS Code specific settings
├── venv/                   # Python virtual environment - IGNORED BY GIT


## Setup Instructions

This project uses Docker for environment consistency and PostgreSQL as its database.

### Prerequisites

* Git
* Python 3.9+ (Python 3.13.4 used in development)
* Docker Desktop (for Windows/macOS) or Docker Engine (for Linux)
* A Telegram account to register an API application.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/telegram-data-pipeline.git](https://github.com/your-username/telegram-data-pipeline.git)
cd telegram-data-pipeline