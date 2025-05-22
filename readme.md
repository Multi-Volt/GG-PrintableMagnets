## MagnetometerApp - 3D Magnetic Field Scanner

This tool was developed by **John Simonis** as part of the **GreyGoo** research project at **The Ohio State University**, supervised by **Dr. John LaRocco** and **Dr. Qudsia Tahmina**. MagnetometerApp is a cross-platform GUI app designed to interface with a custom Arduino-powered magnetic field scanner. It collects, logs, and visualizes full 3D magnetic field vector data from rotational samples using a QMC5883L magnetometer.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Data/Plots/50percent_trial1/50percent_trial1_vector_field_mesh_shrink.png)
---

### Requirements

#### Software

* [Python 3.12+](https://www.python.org/)
* [Arduino IDE](https://www.arduino.cc/en/software)
* [Git](https://git-scm.com/)

Install Python dependencies using:

```bash
pip install -r requirements.txt
```

Key Python libraries include:

* pandas
* numpy
* openpyxl
* matplotlib
* scipy
* pyserial
* tkinter

---

### Build Instructions

First, clone the repository and navigate into the directory:

```bash
git clone --branch MagnetometerApp https://github.com/Multi-Volt/GreyGoo.git MagnetometerApp
cd MagnetometerApp
```

#### Linux

1. Make the build script executable:

```bash
chmod +x build_mag.sh
```

2. Run the build script:

```bash
./build_mag.sh
```

#### Windows

1. Open Command Prompt or PowerShell.
2. Run the build script:

```cmd
build_mag.bat
```

Note: macOS is not officially tested or supported at this time but this could work on that platform.

---

### Running the Application

After setup, navigate to the `src/python/` directory and launch the GUI application:

```bash
python magnetic_logger_gui.py
```

Features of the GUI include:

* Serial port selection
* Sensor calibration
* Rotational data collection
* Trial logging and export
* 3D data visualization

Alternatively, if you had just built the app you could launch the app with:

```bash
./build/magnetic_imager/magnetic_logger_gui/magnetic_logger_gui # For Linux
.\build\magnetic_imager\magnetic_logger_gui\magnetic_logger_gui.exe # For Windows
```
---

### Arduino Firmware

The firmware for the Arduino Nano is located in:

```
src/arduino/arduino.ino
```

Upload this script via the Arduino IDE. It handles real-time communication with the QMC5883L sensor and sends baseline-corrected vector data to the host machine.

---

### Project Structure

```
MagnetometerApp/
├── build_mag.sh / build_mag.bat     # Build scripts
├── requirements.txt                 # Python dependency list
├── src/
│   ├── python/
│   │   ├── magnetic_logger_gui.py   # GUI frontend
│   │   └── magnetic_logger_core.py  # Core data processing & plotting
│   └── arduino/
│       └── arduino.ino              # Firmware for Arduino Nano
├── licenses/
│   ├── LICENSE.txt
│   └── THIRD_PARTY_LICENSES.txt
```

---

### Licensing

This project is licensed under the terms of:

* `licenses/LICENSE.txt`
* `licenses/THIRD_PARTY_LICENSES.txt`

Please review these before redistribution or modification.

---

### Credit

Developed by **John Simonis** as part of the **GreyGoo** research project at **The Ohio State University**, under the supervision of **Dr. John LaRocco** and **Dr. Qudsia Tahmina**.

For academic citation, reproduction, or questions, please contact the author via institutional affiliation.

