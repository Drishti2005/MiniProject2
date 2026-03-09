#!/usr/bin/env python3
"""
Start the backend server
This script ensures proper module imports
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    print("Starting Sidekick Medical Assistant Backend Server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Press CTRL+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
