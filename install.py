import os
import subprocess
import sys
import platform

def main():
    print("☕ Starting PyThumb Optimizer Setup...")
    venv_dir = "venv"

    # 1. Create Virtual Environment
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in '{venv_dir}'...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    else:
        print(f"Virtual environment '{venv_dir}' already exists.")

    # 2. Determine paths based on OS
    if platform.system() == "Windows":
        pip_exe = os.path.join(venv_dir, "Scripts", "pip")
        python_exe = os.path.join(venv_dir, "Scripts", "python")
        activate_cmd = r"venv\Scripts\activate"
    else:
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        python_exe = os.path.join(venv_dir, "bin", "python")
        activate_cmd = "source venv/bin/activate"

    # 3. Install Requirements
    packages = ["PySide6", "Pillow"]
    print(f"\nInstalling packages: {', '.join(packages)}...")
    
    # Upgrade pip first to avoid annoying warning text
    subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    
    # Install required packages
    subprocess.check_call([pip_exe, "install"] + packages)

    print("\n✅ Setup Complete!")
    print("-" * 40)
    print("To start the app, run the following commands:")
    print(f"  1. {activate_cmd}")
    print(f"  2. python main.py")
    print("-" * 40)

if __name__ == "__main__":
    main()
