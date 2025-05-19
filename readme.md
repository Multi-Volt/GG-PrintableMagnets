## MeshMaker - Hollow Mesh Shell Generator

This tool was developed by **John Simonis** as part of the **GreyGoo** research project at **The Ohio State University**, supervised by **Dr. John LaRocco** and **Dr. Qudsia Tahmina**. MeshMaker is a lightweight, cross-platform GUI tool that takes STL files and makes hollow mesh shells and solid mesh cores for physical experimentation and testing. This utility supports direct integration into workflows for constructing physical enclosures and embedding experimental materials such as magnetic compounds.

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/MeshMaker/demo_animation.gif)

![](https://github.com/Multi-Volt/GG-PrintableMagnets/blob/MeshMaker/demo_crosssection.png)

*Note: This demo showcases a multi-material print prepared with MeshMaker. Featured is a pink PETG outer shell and a blue PLA inner shell. *
---

### Requirements

#### Software

* [Go (v1.18+)](https://golang.org/dl/)
* Terminal (Linux) or Command Prompt / PowerShell (Windows)
* Git (optional for the repository)

To verify your Go installation consider running:

```bash
go version
```

If you wish to build this project, please run this command before running any build script:

```bash
go mod tidy
```

---

### Build Instructions

First clone the repository, this can be done easily with:
```bash
git clone --branch MeshMaker https://github.com/Multi-Volt/GG-PrintableMagnets.git MeshMaker
cd MeshMaker
```

#### Linux

1. Make the build script executable:

```bash
chmod +x build.sh
```

2. Build the binary:

```bash
./build.sh
```

The output will be located in the `build/` directory as `hollowblender_linux`.

#### Windows

1. Open Command Prompt or PowerShell.
2. Run the build script:

```cmd
build.bat
```

The output will be located in the `build/` directory as `hollowblender_win.exe`.

Note: macOS is not officially tested or supported at this time.

---

### Running the Application

After a successful build, navigate to the `build/` directory and execute the binary:

```bash
./hollowblender_linux        # For Linux
.\hollowblender_win.exe      # For Windows
```

To view command-line usage and supported flags:

```bash
./hollowblender_linux --help
```

---

### Test STL Files

Example STL files are included in the `testfiles/` directory:

* `TestMesh.stl`
* `TestMesh2.stl`

These can be used to validate the program before using custom models.

---

### Precompiled Binaries

Precompiled executables are available in the `releases/` directory:

* `hollowblender_windows.zip`
* `hollowblender_linux_dev.tar.gz`

Extract the appropriate archive and run the binary directly.

---

### Project Structure

```
MeshMaker/
├── build.sh                  # Linux build script
├── build.bat                 # Windows build script
├── go.mod / go.sum           # Go module definitions
├── src/                      # Source code
│   └── hollow_with_blender_fyne.go
├── testfiles/                # Sample STL models
├── licenses/                 # Legal documents
└── readme.md                 # This document
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

