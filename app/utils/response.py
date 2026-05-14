from __future__ import annotations

from datetime import datetime, timezone

from flask import jsonify


def api_success(data=None, status: int = 200, **meta):
    payload = {
        "success": True,
        "data": data or {},
        "error": None,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            **meta,
        },
    }
    return jsonify(payload), status


def api_error(code: str, message: str, status: int = 400):
    payload = {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message, "status": status},
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
        },
    }
    return jsonify(payload), status
