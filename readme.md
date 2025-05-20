## 3D Printer Settings

#### Shell:

| Category       | Setting                         | Value                 |
|----------------|----------------------------------|------------------------|
| Printer        | Nozzle Diameter                 | 0.4 mm                |
|                | Filament                        | PLA                   |
|                | Layer Height                    | 0.2 mm                |
|                | Seam Alignment                  | Aligned               |
|                | Support / Raft                  | None                  |
| Shells         | Wall Loops                      | 2                     |
|                | Top Layers / Thickness          | 5 / 1.0 mm            |
|                | Bottom Layers / Thickness       | 3 / 0.0 mm            |
| Surface        | Top Pattern                     | Monotonic             |
|                | Bottom Pattern                  | Monotonic             |
| Paint Layers   | Top / Bottom Penetration Layers | 5 / 3                 |
| Infill         | Density                         | 100% (Solid)          |
|                | Pattern (Solid / Sparse)        | Rectilinear / Rectilinear |

#### Magnetometer:

| Category     | Setting                         | Value                       |
|--------------|---------------------------------|-----------------------------|
| Printer      | Nozzle Diameter                 | 0.4 mm                      |
|              | Filament                        | PLA                         |
|              | Layer Height                    | 0.2 mm                      |
|              | Seam Alignment                  | Aligned                     |
|              | Support / Raft                  | None                        |
| Shells       | Wall Loops                      | 2                           |
|              | Top Layers / Thickness          | 5 / 1.0 mm                  |
|              | Bottom Layers / Thickness       | 3 / 0.0 mm                  |
| Surface      | Top Pattern                     | Monotonic                   |
|              | Bottom Pattern                  | Monotonic                   |
| Paint Layers | Top / Bottom Penetration Layers | 5 / 3                       |
| Infill       | Density                         | Variable (Depending on wt%) |
|              | Pattern (Solid / Sparse)        | Rectilinear / Rectilinear   |

*All files were printed on a [Bambu Lab A1](https://www.bambulab.com/en/a1)*

---

## 🛠 Experimental Procedure

The fabrication 3D printed magnets was conducted using a structured workflow. Below is a detailed, step-by-step overview of the process:

---

### 1. Shell Fabrication via Fused Deposition Modeling (FDM)

PLA shells were designed using **MeshMaker** CAD software (see the MeshMaker branch) and processed using **BambuSlicer** for toolpath generation. All shells were printed in a single batch using an FDM 3D printer with [Inland 1.75 mm PLA+ filament](https://www.microcenter.com/product/611538/inland-175mm-pla-3d-printer-filament-10-kg-(22-lbs)-spool-light-blue). This ensured consistent printing conditions and minimized inter-batch variability.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/printed_shells.jpg)

---

### 2. Preparation of Magnetite-Filled Mixtures

An empty plastic container was placed on a digital scale and tared to zero.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/empty_container.jpg)

For each target weight percentage (wt%)—**10%, 30%, and 50%**—magnetite (Fe₃O₄) powder was weighed in approximate amounts of **10 g, 30 g, and 50 g**, respectively.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/50percent_magnetite.jpg)

Once the magnetite was measured, **polyvinyl acetate (PVA) glue** was added until the total mass of the mixture reached approximately **100 g**. This approach maintained the desired magnetite-to-binder ratio for each wt% listed above.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/unmixed_magnetic_solution.jpg)

---

### 3. Homogenization of Magnetic Composite

The magnetite–PVA mixture was stirred manually until a **visually homogeneous** suspension was achieved. This step ensured an even distribution of magnetic particles within the polymer matrix.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/mixed_magnetic_solution.jpg)

---

### 4. Loading of Mixture into Syringe

Once mixed, the composite solution was transferred into a **10 mL disposable syringe** for controlled injection into the PLA Shells.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/filling_syringe.jpg)

---

### 5. Preparation of Printed PLA+ Shells

The printed PLA+ shells were arranged on a **clean, flat working surface**, oriented with their fill ports facing upward to allow for easy injection.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/empty_shell.jpg)

---

### 6. Injection of Magnetic Mixture

Using the preloaded syringe, the magnetic mixture was **injected into each PLA+ shell** until the cavity was fully filled. Care was taken to avoid air bubbles or overflow.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/filling_shell.jpg)

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/filled_shell.jpg)

---

### 7. Magnet Placement

Two **N52-grade neodymium disc magnets** (1.26-inch diameter × ⅛-inch thickness) were placed on opposite sides of each filled shell to arrange the suspended magnetite crystals in the solution.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/setting_with_magnets.jpg)

---

### 8. Replication and Curing

The above steps were repeated until **five complete samples** were prepared for each wt% grouping. Each sample was taped securely to prevent magnet displacement and placed in a **food dehydrator** set to **60 °C for 12 hours** to cure the PVA matrix.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/Media/Images/drying_magnets.jpg)

## 🛠 Testing Procedure

The testing of the 3D-printed magnetic composite shells was carried out using a custom-built magnetic field scanner designed to measure the spatial characteristics of magnetic fields in a precise, repeatable manner. This section outlines the construction, calibration, operation, and data processing pipeline in full detail.

---

### 1. Magnetic Field Scanner Overview

The magnetic scanner was built around the following core hardware components:

* **Arduino Nano** microcontroller
* **QMC5883L 3-axis digital magnetometer**
* **28BYJ-48 stepper motor** driven by a **ULN2003 motor driver board**
* **Custom-built PLA turntable**, supported by three **608-style skateboard bearings**
* **Stainless steel 304 threaded rod (M5 x 200 mm)** for vertical positioning of the sensor
* **5 mm to 8 mm aluminum shaft coupler** to secure the sensor rod to a static base
* **Painter's tape alignment crosshair** for consistent sample positioning

This configuration allowed for full 360° magnetic vector field data acquisition around the samples, with adjustable sensor height and a fixed radial offset from the sample.

---

### 2. Sensor Mounting and Geometry

The **QMC5883L magnetometer** was rigidly fixed to a vertically mounted threaded rod via a PLA bracket, which allowed precise adjustment of sensor height relative to the sample. For this experiment, measurements were taken at two discrete vertical distances:

* **0 cm height:** Center-aligned with the horizontal plane of the turntable
* **2 cm height:** Aligned with the top of the PLA+ cubes (20 mm edge length)

The **radial distance** of the sensor was fixed at **2 cm away from the center** of the turntable throughout testing. This configuration approximated the behavior of magnetic fields at realistic distances relevant to application use cases.

---

### 3. Arduino Firmware and Calibration Logic

The Arduino Nano was flashed with custom firmware written in C++, leveraging the `QMC5883LCompass`, `CheapStepper`, and `EEPROM` libraries.

#### Calibration Procedure:

* Calibration was initiated by sending the character `'c'` via serial to the Arduino.
* The system captured **1,000 magnetic field vector readings** (X, Y, Z) in microtesla (µT).
* A baseline offset was calculated and saved to **non-volatile EEPROM**.

```cpp
B_X0 = sumX / SAMPLE_COUNT;
B_Y0 = sumY / SAMPLE_COUNT;
B_Z0 = sumZ / SAMPLE_COUNT;
EEPROM.put(...);
```

These offsets were subtracted from all future readings to null out Earth’s geomagnetic field and static bias.

#### Measurement Procedure:

* Measurement began when `'r'` was sent over serial.

* For each angle (0° to 359°), the magnetometer:

  * Acquired and baseline-corrected the (X, Y, Z) field components.

  * Calculated the **magnitude** of the field as:

    ```cpp
    float mag = sqrt((long)dx * dx + (long)dy * dy + (long)dz * dz);
    ```

  * Transmitted data over serial in the format:

    ```
    <angle> | <B_x> <B_y> <B_z> | <magnitude>
    ```

* The stepper motor is then continuously advanced by one degree (approx. 11.38 microsteps), for a full 360° sweep.

* After 360 steps, a configurable offset (e.g., 150 steps) was applied to return to origin alignment due to skipped steps.

---

### 4. Sample Placement and Alignment

Each magnetically-filled PLA+ cube was placed in the center of the turntable. Painter’s tape was used to create a centered crosshair target on the turntable, ensuring consistent alignment between trials.

---

### 5. GUI-Controlled Python Application

A custom Python application with a **Tkinter GUI** was developed to interface with the magnetometer system.

**Core features:**

* Connect and communicate with the Arduino over serial (9600 baud)
* Trigger calibration and measurement via buttons
* Log live readings to console and graphical interface
* Save all data to an **Excel workbook** with detailed headers
* Provide real-time progress feedback

**Excel columns included:**

* Trial name
* Rotation angle (degrees)
* Sensor height (cm)
* Radial distance (cm)
* B\_x, B\_y, B\_z (in µT and G)
* Vector magnitude (in µT and G)

Conversion from µT to Gauss was done via the relation:

```
1 µT = 0.01 Gauss
```

---

### 6. Data Visualization

After each trial, the application allowsto generate 3D plots of the magnetic field using `matplotlib`. The user could select one of four visualization modes:

1. **Scalar Field**: Magnetic field magnitudes plotted as color-coded points
2. **Unit Vector Field**: Normalized direction vectors showing field orientation
3. **True Vector Field**: Scaled vectors proportional to field strength
4. **Deformed Mesh**: A radial mesh where each point is “shrunk” based on field magnitude

The visualizations were color-mapped using `viridis` and output as high-resolution `.png` files. Mesh deformation used spline interpolation via `RectBivariateSpline` to generate smooth surfaces across heights and angles.

---

### 7. Trial Conditions and Reproducibility

Each magnetic shell underwent multiple measurement trials. The key experimental conditions were as follows:

| Parameter            | Value                                   |
|----------------------|-----------------------------------------|
| Sensor Heights       | 0 cm and 2 cm                           |
| Radial Offset        | 2 cm from turntable center              |
| Turntable Resolution | 360 steps (1° increments)               |
| Sensor               | QMC5883L digital magnetometer           |
| Samples              | 5 total PLA+ magnetic cubes per wt%     |
| Stepper Type         | 28BYJ-48 (ULN2003 driver)               |
| Sensor Mount         | M5 threaded rod, rigid mount            |
| Measurement Unit     | Microtesla (µT), converted to Gauss (G) |

---

### 8. Video Demo

[![CLICK ME](https://i3.ytimg.com/vi/pRHvHz7wCB8/maxresdefault.jpg)](https://youtu.be/pRHvHz7wCB8)

