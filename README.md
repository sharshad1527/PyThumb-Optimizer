# PyThumb Optimizer ☕

A sleek, PySide6-based desktop application designed specifically for content creators. It provides a lightning-fast workflow to perfectly crop, stretch, and optimize images into 1280x720 YouTube thumbnails while strictly enforcing the 2MB file size limit.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

## 📥 Download the App

Don't want to mess with Python or code? **[Download the ready-to-use app from the Releases tab!](../../releases/latest)**

* **Windows Users:** Download the `.exe` file. Place it anywhere and double-click to run.
* **Linux Users:** Download the Linux binary. Make sure it has executable permissions (`chmod +x PyThumb-Optimizer`) and run it directly in your terminal or by double-clicking. No installation required.

---

## ✨ Key Features

* **Interactive 16:9 Cropping:** Drag and resize a strictly enforced 16:9 bounding box to frame your thumbnail perfectly.
* **Stretch Mode:** Instantly toggle to "Stretch Mode" to force-fit any image into the 1280x720 resolution without cropping.
* **Smart 2MB Auto-Compression:** Never get a "File too large" error again. The app saves high-quality PNGs by default, but automatically switches to JPG and downscales quality in 5% increments if the image exceeds YouTube's 2MB limit.
* **Drag & Drop Workflow:** Bypass the file picker. Drag any image directly onto the canvas to start editing instantly.
* **Premium UI/UX:** Features a custom, dark "espresso/coffee" themed interface designed for late-night editing sessions.

---

## 🚀 Running from Source (For Developers)

If you want to run the raw Python code or modify the tool, use the automated setup script.

**1. Clone the repository:**
```bash
git clone https://github.com/sharshad1527/PyThumb-Optimizer.git
cd PyThumb-Optimizer
```

**2. Run the automated installer:**

```bash
python install.py

```

*(This script will automatically detect your OS, create a virtual environment, and install PySide6 and Pillow).*

**3. Activate the environment and run:**

* **Windows:**
```cmd
venv\Scripts\activate
python main.py

```


* **Linux/macOS:**
```bash
source venv/bin/activate
python main.py

```

---

## 🛠️ Building the Executables Yourself

If you modify the code and want to build your own standalone applications, activate your virtual environment, install PyInstaller (`pip install pyinstaller`), and run the following commands:

**For Windows (Run on a Windows machine):**

```cmd
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

**For Linux (Run on a Linux machine):**
```Bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico:." main.py
```

*Your standalone application will be generated in the `dist/` folder.*

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make to this project are **greatly appreciated**.

If you have a suggestion that would make this app better:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

You can also simply open an issue with the tag "enhancement" to drop some ideas!
