import os
import sys
from pathlib import Path

def main():
    """Helper script to run the Streamlit application."""
    project_root = Path(__file__).parent
    main_script = project_root / "src" / "geovoto" / "main.py"
    
    if not main_script.exists():
        print(f"Error: Could not find main script at {main_script}")
        sys.exit(1)
        
    print(f"Starting GeoVoto from {main_script}...")
    
    # Add src to PYTHONPATH
    src_path = project_root / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

    # Execute streamlit run command with modified environment
    # We use subprocess instead of os.system to pass environment
    import subprocess
    subprocess.run(["streamlit", "run", str(main_script)], env=env)

if __name__ == "__main__":
    main()
