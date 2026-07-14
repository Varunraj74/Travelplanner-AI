"""
TravelPlannerPro - Application Entry Point
IBM SkillsBuild Final Project | Edunet Foundation
Problem Statement No. 5 – Travel Planner Agent
"""

import os
import sys
import logging
from app import create_app

# ─── Logging Configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("TravelPlannerPro")

# ─── Create Flask Application ─────────────────────────────────────────────────
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"

    logger.info("=" * 60)
    logger.info("  TravelPlannerPro – AI-Powered Travel Planner")
    logger.info("  IBM Granite | IBM watsonx.ai | Flask")
    logger.info("=" * 60)
    logger.info(f"  Server running at: http://localhost:{port}")
    logger.info(f"  Debug mode: {debug}")
    logger.info("=" * 60)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
