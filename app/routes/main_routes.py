"""
TravelPlannerPro - Main Routes
Serves the HTML pages for the web application.
"""

import logging
from flask import Blueprint, render_template, current_app

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing page — hero section with CTA to start planning."""
    return render_template(
        "index.html",
        app_name=current_app.config.get("APP_NAME", "TravelPlannerPro"),
        app_tagline=current_app.config.get("APP_TAGLINE", ""),
        demo_mode=current_app.config.get("DEMO_MODE", True),
        model_id=current_app.config.get("IBM_MODEL_ID", "ibm/granite-13b-instruct-v2"),
    )


@main_bp.route("/dashboard")
def dashboard():
    """Travel planning dashboard — form to enter trip details."""
    return render_template(
        "dashboard.html",
        app_name=current_app.config.get("APP_NAME", "TravelPlannerPro"),
        demo_mode=current_app.config.get("DEMO_MODE", True),
        model_id=current_app.config.get("IBM_MODEL_ID", "ibm/granite-13b-instruct-v2"),
    )


@main_bp.route("/workspace")
def workspace():
    """Workspace — itinerary viewer and AI chat assistant."""
    return render_template(
        "workspace.html",
        app_name=current_app.config.get("APP_NAME", "TravelPlannerPro"),
        demo_mode=current_app.config.get("DEMO_MODE", True),
        model_id=current_app.config.get("IBM_MODEL_ID", "ibm/granite-13b-instruct-v2"),
    )
