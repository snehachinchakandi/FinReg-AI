"""
FinReg AI — Enterprise Regulatory Intelligence Platform Launcher.
Runs the unified FastAPI backend and serves the compiled modern React SPA.

Usage:
    python run_platform.py             # Runs production unified server on http://localhost:8000
    python run_platform.py --port 8080 # Runs on custom port
"""

import argparse
import sys
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description="FinReg AI Platform Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload for development")
    args = parser.parse_args()

    print("=" * 70)
    print("⚖️  FinReg AI: Indian Financial Regulation Intelligence Platform")
    print(f"🚀  Serving on http://{args.host}:{args.port}")
    print("=" * 70)
    print("   • Unified Web Cockpit: http://127.0.0.1:8000")
    print("   • REST API Swagger UI: http://127.0.0.1:8000/docs")
    print("   • Regulatory Documents: http://127.0.0.1:8000/api/documents")
    print("   • Temporal Evolution:  http://127.0.0.1:8000/api/evolution/timeline")
    print("=" * 70)

    uvicorn.run(
        "app.backend.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
