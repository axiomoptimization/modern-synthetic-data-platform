from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_RANDOM_SEED = 42

BRONZE_DIR_NAME = "bronze"
SILVER_DIR_NAME = "silver"
GOLD_DIR_NAME = "gold"

SUPPORTED_ENTITIES = ("customers", "agents", "policies", "claims", "payments")
