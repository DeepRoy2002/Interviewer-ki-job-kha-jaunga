import os
import sys
import subprocess

if __name__ == "__main__":
    print("Starting AI-Powered Interview Mentoring Platform...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "frontend", "app.py")
    
    # Using subprocess to invoke streamlit run
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", app_path]))
