import os
import subprocess
import sys

try:
    # Create virtual environment if it doesn't exist
    if not os.path.exists(".venv"):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
        print("Virtual environment created.")

    # Install requirements
    python_exe = os.path.join(".venv", "Scripts" if os.name == "nt" else "bin", "python")

    print("Installing requirements...")
    requirements_path = os.path.join("scripts", "requirements.txt")
    subprocess.check_call([python_exe, "-m", "pip", "install", "-r", requirements_path])

    print("Requirements installed successfully.")
except Exception as e:
    print(f"An error occurred: {e}")

print("")
input("Press Enter to continue...")
