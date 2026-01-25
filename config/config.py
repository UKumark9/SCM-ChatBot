"""
Configuration File for SCM Chatbot
Centralizes all settings, API keys, and parameters
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# LLM Configuration
LLM_CONFIG = {
    "provider": "groq",
    "model_name": "llama3-70b-8192",
    "temperature": 0.1,
    "max_tokens": 4096,
    "api_key": os.getenv("GROQ_API_KEY")
}

# Vector Database Configuration
VECTOR_DB_CONFIG = {
    "provider": "faiss",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384,
    "index_path": str(MODELS_DIR / "faiss_index")
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.7
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    "delay_threshold_days": 5,
    "inventory_low_threshold": 10,
    "inventory_high_threshold": 1000,
    "forecast_periods": 30
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "secret_key": "your-secret-key-change-in-production"
}

# UI Configuration
UI_CONFIG = {
    "title": "AI-Powered Supply Chain Management Chatbot",
    "description": "Ask questions about orders, inventory, suppliers, and logistics",
    "theme": "default",
    "share": False
}

# Dataset Paths
DATASET_PATHS = {
    "train": {
        "orders": str(DATA_DIR / "train" / "df_Orders.csv"),
        "customers": str(DATA_DIR / "train" / "df_Customers.csv"),
        "products": str(DATA_DIR / "train" / "df_Products.csv"),
        "order_items": str(DATA_DIR / "train" / "df_OrderItems.csv"),
        "payments": str(DATA_DIR / "train" / "df_Payments.csv")
    },
    "test": {
        "orders": str(DATA_DIR / "test" / "df_Orders.csv"),
        "customers": str(DATA_DIR / "test" / "df_Customers.csv"),
        "products": str(DATA_DIR / "test" / "df_Products.csv"),
        "order_items": str(DATA_DIR / "test" / "df_OrderItems.csv"),
        "payments": str(DATA_DIR / "test" / "df_Payments.csv")
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "scm_chatbot.log"),
            "formatter": "standard"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
}

# Agent Configuration
AGENT_CONFIG = {
    "max_iterations": 10,
    "timeout": 60,
    "verbose": True
}

# Evaluation Metrics Thresholds
EVAL_THRESHOLDS = {
    "accuracy": 0.85,
    "mape": 15.0,
    "rmse": 10.0,
    "latency": 2.0,
    "hallucination_rate": 0.05
}
