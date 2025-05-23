# forest_app/config/settings.py
# MODIFIED FOR PYDANTIC V1 COMPATIBILITY

import logging
import os
import secrets
from typing import Any, Dict, Optional

# Import BaseSettings from Pydantic V1 and Extra for config
from pydantic import BaseSettings, Extra

logger = logging.getLogger(__name__)


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables using Pydantic V1 BaseSettings.
    Includes configurations for specific engines AND feature flags.
    Ensures all flags defined in Feature Enum have a corresponding setting.
    """

    # --- Required environment variables ---
    GOOGLE_API_KEY: str
    DB_CONNECTION_STRING: str
    SECRET_KEY: str = secrets.token_hex(32)  # 256-bit secret key
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT != "production"

    # --- Optional with defaults (Core LLM/App) ---
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash-latest"
    GEMINI_ADVANCED_MODEL_NAME: str = "gemini-1.5-pro-latest"
    LLM_TEMPERATURE: float = 0.7

    # --- Optional Engine Configurations ---
    # (These configure engines IF they are enabled by flags below)
    METRICS_ENGINE_ALPHA: float = 0.3
    METRICS_ENGINE_THRESHOLDS: Optional[Dict[str, float]] = None
    NARRATIVE_ENGINE_CONFIG: Optional[Dict[str, Any]] = None
    SNAPSHOT_FLOW_FREQUENCY: int = 5
    SNAPSHOT_FLOW_MAX_SNAPSHOTS: int = 100
    TASK_ENGINE_TEMPLATES: Optional[Dict[str, Any]] = None
    # PRACTICAL_CONSEQUENCE_CALIBRATION: Optional[Dict[str, float]] = None

    # --- Feature Flags ---
    # Default values represent a Bare Bones MVP target state.
    # Override via environment variables or .env file.

    # Core Functionality - Assumed ON unless specifically disabled for tests
    FEATURE_ENABLE_CORE_ONBOARDING: bool = True
    FEATURE_ENABLE_CORE_HTA: bool = True
    FEATURE_ENABLE_CORE_TASK_ENGINE: bool = True

    # Deferred / Potentially ON for MVP
    FEATURE_ENABLE_XP_MASTERY: bool = True
    FEATURE_ENABLE_MEMORY_SYSTEM: bool = True

    # Modules with Flag Integration Added (Default OFF for MVP, except where noted)
    FEATURE_ENABLE_DEVELOPMENT_INDEX: bool = False
    FEATURE_ENABLE_ARCHETYPES: bool = False
    FEATURE_ENABLE_SENTIMENT_ANALYSIS: bool = False
    FEATURE_ENABLE_NARRATIVE_MODES: bool = False
    FEATURE_ENABLE_PATTERN_ID: bool = True
    FEATURE_ENABLE_SHADOW_ANALYSIS: bool = False
    FEATURE_ENABLE_TRAIL_MANAGER: bool = False
    FEATURE_ENABLE_SOFT_DEADLINES: bool = False
    FEATURE_ENABLE_TRIGGER_PHRASES: bool = True
    FEATURE_ENABLE_HARMONIC_RESONANCE: bool = False
    FEATURE_ENABLE_RESISTANCE_ENGINE: bool = False
    FEATURE_ENABLE_EMOTIONAL_INTEGRITY: bool = False
    FEATURE_ENABLE_RELATIONAL: bool = False
    FEATURE_ENABLE_REWARDS: bool = False
    FEATURE_ENABLE_FINANCIAL_READINESS: bool = False
    FEATURE_ENABLE_DESIRE_ENGINE: bool = False
    FEATURE_ENABLE_PRACTICAL_CONSEQUENCE: bool = False
    FEATURE_ENABLE_TASK_RESOURCE_FILTER: bool = False
    FEATURE_ENABLE_POETIC_ARBITER_VOICE: bool = True
    FEATURE_ENABLE_HTA_VISUALIZATION: bool = True
    FEATURE_ENABLE_WITHERING: bool = False

    # Flags Defined But Not Used in Code Checks (Skipped based on discussion)
    FEATURE_ENABLE_LOGGING_TRACKING: bool = True
    FEATURE_ENABLE_SNAPSHOT_FLOW: bool = True
    FEATURE_ENABLE_METRICS_SPECIFIC: bool = True
    FEATURE_ENABLE_HARMONIC_FRAMEWORK: bool = False

    # Pydantic V1 Settings Configuration
    class Config:
        env_file = ".env"  # Load from .env file if it exists
        env_file_encoding = "utf-8"
        extra = Extra.ignore  # Ignore extra environment variables not defined in the model


# --- Create a single instance of the settings ---
settings = AppSettings()

# --- Logging & Checks (Keep your existing checks) ---
logger.debug(">>> DEBUG SETTINGS (Pydantic V1): STARTING Pydantic settings.py <<<")
# For Pydantic V1, model_dump() is just .dict()
for key, value in settings.dict().items():
    if "KEY" in key.upper() or "STRING" in key.upper() or "TOKEN" in key.upper(): # Made check case-insensitive
        logger.debug(
            f">>> DEBUG SETTINGS: {key}: {'Loaded' if value else 'Missing/Empty'}"
        )
    else:
        logger.debug(f">>> DEBUG SETTINGS: {key}: {value}")

if not settings.GOOGLE_API_KEY:
    logger.critical(">>> CRITICAL SETTINGS: GOOGLE_API_KEY is missing!")
if not settings.DB_CONNECTION_STRING:
    logger.critical(">>> CRITICAL SETTINGS: DB_CONNECTION_STRING is missing!")
logger.debug(">>> DEBUG SETTINGS (Pydantic V1): END OF Pydantic settings.py <<<")
