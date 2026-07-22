"""Optional convenience launcher.

The app runs with a single command:

    streamlit run app.py

This script is an alternative entry point that does a couple of friendly
sanity checks (e.g. warns if `.env` is missing) before launching Streamlit:

    python run.py
"""
import os
import subprocess
import sys


def main() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_root, ".env")

    if not os.path.exists(env_path):
        print(
            "⚠️  No .env file found. Copy .env.example to .env and fill in "
            "your MySQL and Anthropic settings before running the app.\n"
        )

    app_path = os.path.join(project_root, "app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    print(f"Starting AI Insight Studio...\n  {' '.join(cmd)}\n")
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
