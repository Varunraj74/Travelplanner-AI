"""
TravelPlannerPro - API Routes
All REST API endpoints for travel planning and chat functionality.
All responses follow the format: {"success": bool, "data": {}} or {"success": false, "error": "msg"}
"""

import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, session, send_file

from app.services.travel_service import TravelService
from app.utils.validators import validate_travel_form, validate_chat_message, sanitize_string
from app.utils.pdf_generator import generate_travel_pdf

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)

# Shared service instance (per-process)
_travel_service = TravelService()


# ─── Health Check ─────────────────────────────────────────────────────────────

@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "success": True,
        "data": {
            "status": "healthy",
            "app": current_app.config.get("APP_NAME"),
            "version": current_app.config.get("APP_VERSION"),
            "demo_mode": current_app.config.get("DEMO_MODE", True),
            "model_id": current_app.config.get("IBM_MODEL_ID"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    })


# ─── Generate Itinerary ───────────────────────────────────────────────────────

@api_bp.route("/generate-itinerary", methods=["POST"])
def generate_itinerary():
    """
    Generate a complete AI travel itinerary.

    Request body (JSON):
        source, destination, departure_date, return_date, travelers,
        budget, interests, transport, hotel_pref, travel_style, special_requests

    Returns:
        {"success": true, "data": {"itinerary": "...", "demo_mode": bool}}
    """
    try:
        data = request.get_json(silent=True) or {}

        # Validate input
        is_valid, errors = validate_travel_form(data)
        if not is_valid:
            return jsonify({"success": False, "error": "Validation failed", "fields": errors}), 400

        # Sanitize inputs
        travel_data = {
            "source": sanitize_string(data.get("source", ""), 100),
            "destination": sanitize_string(data.get("destination", ""), 100),
            "departure_date": sanitize_string(data.get("departure_date", ""), 20),
            "return_date": sanitize_string(data.get("return_date", ""), 20),
            "travelers": int(data.get("travelers", 1)),
            "budget": sanitize_string(data.get("budget", "Medium"), 50),
            "interests": sanitize_string(data.get("interests", ""), 500),
            "transport": sanitize_string(data.get("transport", "any"), 50),
            "hotel_pref": sanitize_string(data.get("hotel_pref", "mid-range"), 50),
            "travel_style": sanitize_string(data.get("travel_style", "leisure"), 50),
            "special_requests": sanitize_string(data.get("special_requests", ""), 500),
        }

        # Store in session for PDF generation and chat context
        session["travel_data"] = travel_data
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())

        logger.info(
            f"Generating itinerary: {travel_data['source']} → {travel_data['destination']} "
            f"(travelers={travel_data['travelers']}, budget={travel_data['budget']})"
        )

        result = _travel_service.generate_itinerary(travel_data)

        return jsonify({
            "success": True,
            "data": {
                "itinerary": result["itinerary"],
                "demo_mode": result["demo_mode"],
                "model_id": result["model_id"],
                "destination": travel_data["destination"],
                "source": travel_data["source"],
                "trip_duration": _calculate_duration(
                    travel_data["departure_date"], travel_data["return_date"]
                ),
            }
        })

    except Exception as e:
        logger.error(f"Itinerary generation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to generate itinerary. Please try again."}), 500


# ─── Chat Assistant ───────────────────────────────────────────────────────────

@api_bp.route("/chat", methods=["POST"])
def chat():
    """
    AI travel chat assistant endpoint.

    Request body (JSON):
        message: str

    Returns:
        {"success": true, "data": {"response": "...", "demo_mode": bool}}
    """
    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()

        # Validate message
        is_valid, error_msg = validate_chat_message(message)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400

        # Ensure session has an ID
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())

        session_id = session["session_id"]
        travel_context = session.get("travel_data", {})

        result = _travel_service.chat(
            session_id=session_id,
            user_message=message,
            travel_context=travel_context,
        )

        return jsonify({
            "success": True,
            "data": {
                "response": result["response"],
                "demo_mode": result["demo_mode"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        })

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Chat service unavailable. Please try again."}), 500


@api_bp.route("/chat/clear", methods=["POST"])
def clear_chat():
    """Clear the conversation history for the current session."""
    try:
        session_id = session.get("session_id", "")
        if session_id:
            _travel_service.clear_chat_history(session_id)
        return jsonify({"success": True, "data": {"message": "Chat history cleared."}})
    except Exception as e:
        logger.error(f"Chat clear error: {e}")
        return jsonify({"success": False, "error": "Failed to clear chat history."}), 500


# ─── PDF Export ───────────────────────────────────────────────────────────────

@api_bp.route("/export-pdf", methods=["POST"])
def export_pdf():
    """
    Generate and download a professional travel report PDF.

    Request body (JSON):
        itinerary: str (the generated itinerary text)
        travel_data: dict (trip details — optional, falls back to session)

    Returns:
        PDF file download.
    """
    try:
        data = request.get_json(silent=True) or {}
        itinerary_text = data.get("itinerary", "")

        if not itinerary_text:
            return jsonify({"success": False, "error": "No itinerary content provided."}), 400

        # Use provided travel_data or fall back to session
        travel_data = data.get("travel_data") or session.get("travel_data", {})

        # Generate unique filename
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = sanitize_string(travel_data.get("destination", "trip"), 30).replace(" ", "_")
        filename = f"TravelPlan_{destination}_{ts}.pdf"

        export_dir = current_app.config.get("PDF_UPLOAD_FOLDER", "static/exports")
        output_path = os.path.join(export_dir, filename)

        success = generate_travel_pdf(travel_data, itinerary_text, output_path)

        if not success:
            return jsonify({
                "success": False,
                "error": "PDF generation failed. ReportLab may not be installed."
            }), 500

        return send_file(
            output_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        logger.error(f"PDF export error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "PDF export failed. Please try again."}), 500


# ─── Status Endpoint ──────────────────────────────────────────────────────────

@api_bp.route("/status", methods=["GET"])
def status():
    """Return application and IBM integration status."""
    return jsonify({
        "success": True,
        "data": {
            "app_name": current_app.config.get("APP_NAME"),
            "version": current_app.config.get("APP_VERSION"),
            "ai_mode": not current_app.config.get("DEMO_MODE", True),
            "demo_mode": current_app.config.get("DEMO_MODE", True),
            "model_id": current_app.config.get("IBM_MODEL_ID"),
            "endpoint": current_app.config.get("IBM_ENDPOINT_URL"),
            "ibm_sdk_available": _check_ibm_sdk(),
        }
    })


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _calculate_duration(departure: str, return_date: str) -> str:
    """Calculate trip duration in days."""
    try:
        from datetime import datetime as dt
        d1 = dt.strptime(departure, "%Y-%m-%d")
        d2 = dt.strptime(return_date, "%Y-%m-%d")
        delta = (d2 - d1).days
        return f"{delta} day{'s' if delta != 1 else ''}"
    except Exception:
        return "N/A"


def _check_ibm_sdk() -> bool:
    """Check if IBM watsonx.ai SDK is installed."""
    try:
        import ibm_watsonx_ai  # noqa: F401
        return True
    except ImportError:
        return False
