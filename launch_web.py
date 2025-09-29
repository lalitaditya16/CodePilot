#!/usr/bin/env python3
"""
Quick launch script for the Streamlit web interface.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    app_path = script_dir / "streamlit_app.py"
    
    if not app_path.exists():
        print("❌ Error: streamlit_app.py not found!")
        sys.exit(1)
    
    print("🚀 Launching AI Python Code Generator Web Interface...")
    print("📍 App will open in your default browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], cwd=script_dir)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except FileNotFoundError:
        print("❌ Error: Streamlit not installed!")
        print("📦 Install with: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()