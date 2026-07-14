"""
TravelPlannerPro - Flask Application Factory
"""

import os
import logging
from flask import Flask
from config import get_config

logger = logging.getLogger(__name__)


def create_app():
    """
    Flask application factory.
    Creates and configures the Flask app instance.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )

    # ─── Load Configuration ───────────────────────────────────────────────────
    cfg = get_config()
    app.config.from_object(cfg)

    # ─── Ensure Export Directory Exists ──────────────────────────────────────
    export_dir = app.config.get("PDF_UPLOAD_FOLDER", "static/exports")
    os.makedirs(export_dir, exist_ok=True)

    # ─── Validate IBM Credentials ─────────────────────────────────────────────
    _validate_ibm_credentials(app)

    # ─── Register Blueprints ──────────────────────────────────────────────────
    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    logger.info("TravelPlannerPro application initialized successfully.")
    return app


def _validate_ibm_credentials(app: Flask) -> None:
    """
    Validate IBM watsonx.ai credentials at startup.
    Sets DEMO_MODE flag if credentials are missing.
    """
    api_key = app.config.get("IBM_API_KEY", "")
    project_id = app.config.get("IBM_PROJECT_ID", "")
    endpoint = app.config.get("IBM_ENDPOINT_URL", "")

    missing = []
    if not api_key:
        missing.append("IBM_API_KEY")
    if not project_id:
        missing.append("IBM_PROJECT_ID")
    if not endpoint:
        missing.append("IBM_ENDPOINT_URL")

    if missing:
        app.config["DEMO_MODE"] = True
        logger.warning(
            f"IBM credentials missing: {', '.join(missing)}. "
            "Running in DEMO MODE with pre-configured sample responses."
        )
    else:
        app.config["DEMO_MODE"] = False
        logger.info("IBM watsonx.ai credentials validated. AI mode active.")
