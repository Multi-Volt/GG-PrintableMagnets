// Copyright (c) 2025, John Simonis
// This code was written by John Simonis for the GreyGoo research project at The Ohio State University.
// See LICENSE.txt for more information.

package main

import (
	"archive/zip"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/data/binding"
)

// URLs for Blender builds based on OS/architecture
var blenderURLs = map[string]map[string]string{
	"linux": {
		"amd64": "https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-x64.tar.xz",
		"arm64": "https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-arm64.tar.xz",
	},
	"windows": {
		"amd64": "https://download.blender.org/release/Blender4.1/blender-4.1.1-windows-x64.zip",
	},
}

// Return install directory for Blender
func getInstallDir() (string, error) {
	exePath, err := os.Executable()
	if err != nil {
		return "", err
	}
	return filepath.Join(filepath.Dir(exePath), "blender"), nil
}

// Recursively locate the Blender executable inside the install directory
func findBlenderExe(installDir string) (string, error) {
	exeName := "blender"
	if runtime.GOOS == "windows" {
		exeName = "blender.exe"
	}
	var hit string
	err := filepath.Walk(installDir, func(p string, fi os.FileInfo, _ error) error {
		if fi != nil && !fi.IsDir() && filepath.Base(p) == exeName {
			hit = p
			return io.EOF // early exit
		}
		return nil
	})
	if errors.Is(err, io.EOF) {
		err = nil
	}
	return hit, err
}

// Download and extract Blender if not already available
func downloadAndExtractBlender(log func(string)) (string, error) {
	installDir, err := getInstallDir()
	if err != nil {
		return "", err
	}
	if exe, _ := findBlenderExe(installDir); exe != "" {
		log("Found existing Blender → " + exe)
		return exe, nil
	}

	sys, arch := runtime.GOOS, runtime.GOARCH
	url, ok := blenderURLs[sys][arch]
	if !ok {
		return "", fmt.Errorf("no Blender build for %s/%s", sys, arch)
	}

	log("Downloading Blender from " + url)
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("download failed: %s", resp.Status)
	}

	tmp, err := os.CreateTemp("", "blender-*.archive")
	if err != nil {
		return "", err
	}
	defer os.Remove(tmp.Name())
	if _, err := io.Copy(tmp, resp.Body); err != nil {
		return "", err
	}
	tmp.Close()

	_ = os.RemoveAll(installDir)
	if err := os.MkdirAll(installDir, 0o755); err != nil {
		return "", err
	}

	// Handle ZIP and TAR.XZ archives differently
	if filepath.Ext(url) == ".zip" {
		r, err := zip.OpenReader(tmp.Name())
		if err != nil {
			return "", err
		}
		defer r.Close()
		for _, f := range r.File {
			target := filepath.Join(installDir, f.Name)
			if f.FileInfo().IsDir() {
				if err := os.MkdirAll(target, f.Mode()); err != nil {
					return "", err
				}
				continue
			}
			if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
				return "", err
			}
			inF, err := f.Open()
			if err != nil {
				return "", err
			}
			outF, err := os.OpenFile(target, os.O_CREATE|os.O_WRONLY, f.Mode())
			if err != nil {
				inF.Close()
				return "", err
			}
			if _, err := io.Copy(outF, inF); err != nil {
				inF.Close()
				outF.Close()
				return "", err
			}
			inF.Close()
			outF.Close()
		}
	} else {
		if err := exec.Command("tar", "xfJ", tmp.Name(), "-C", installDir).Run(); err != nil {
			return "", err
		}
	}

	exe, err := findBlenderExe(installDir)
	if err != nil || exe == "" {
		return "", fmt.Errorf("blender executable not found after extraction")
	}
	log("Blender installed → " + exe)
	return exe, nil
}

// Generate a shell and core mesh using Blender CLI and a Python job script
func hollowAndCore(blenderExe, inSTL, outShell, outCore string,
	wall float64, log func(string)) error {

	blenderDir := filepath.Dir(blenderExe)
	jobPath := filepath.Join(blenderDir, "job.py")

	// Python script string to hollow the mesh inside Blender
	python := `import bpy, sys, os
in_file, shell_file, core_file, WALL = sys.argv[-4:]
WALL = float(WALL); GAP = 0.0

bpy.ops.wm.read_factory_settings(use_empty=True)
before = set(bpy.data.objects)
bpy.ops.import_mesh.stl(filepath=in_file)
sources = [o for o in bpy.data.objects if o not in before and o.type == 'MESH' and o.data.vertices]
if not sources: raise RuntimeError("No mesh geometry found in input STL")

shell_objs, core_objs = [], []
for src in sources:
    core = src.copy(); core.data = src.data.copy()
    bpy.context.collection.objects.link(core)

    bpy.context.view_layer.objects.active = src
    sh = src.modifiers.new('Shell','SOLIDIFY')
    sh.thickness, sh.offset, sh.use_even_offset, sh.use_quality_normals = WALL,-1,True,True
    bpy.ops.object.modifier_apply(modifier=sh.name)
    shell_objs.append(src)

    bpy.context.view_layer.objects.active = core
    bo = core.modifiers.new('Cavity','BOOLEAN')
    bo.operation, bo.solver, bo.object = 'DIFFERENCE','EXACT',src
    bpy.ops.object.modifier_apply(modifier=bo.name)
    core_objs.append(core)

for p in (shell_file, core_file):
    d = os.path.dirname(os.path.abspath(p))
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
for o in shell_objs: o.select_set(True)
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
bpy.ops.export_mesh.stl(filepath=shell_file, ascii=False, use_selection=True)

bpy.ops.object.select_all(action='DESELECT')
for o in core_objs: o.select_set(True)
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
bpy.ops.export_mesh.stl(filepath=core_file, ascii=False, use_selection=True)
`

	if err := os.WriteFile(jobPath, []byte(python), 0o644); err != nil {
		return err
	}

	absIn, _ := filepath.Abs(inSTL)
	absShell, _ := filepath.Abs(outShell)
	absCore, _ := filepath.Abs(outCore)

	cmd := exec.Command(blenderExe, "-noaudio", "-b",
		"-P", jobPath, "--",
		absIn, absShell, absCore,
		fmt.Sprintf("%f", wall),
	)
	cmd.Stdout, cmd.Stderr, cmd.Dir = os.Stdout, os.Stderr, blenderDir
	if err := cmd.Run(); err != nil {
		return err
	}
	log(fmt.Sprintf("✓ Wrote %s and %s", outShell, outCore))
	return nil
}

// Start the GUI using the Fyne framework
func runGUI() {
	a := app.New()
	w := a.NewWindow("Hollow With Blender")
	w.Resize(fyne.NewSize(1024, 768))

	// Input fields for file paths and wall thickness
	inEntry := widget.NewEntry()
	shellEntry := widget.NewEntry()
	coreEntry := widget.NewEntry()
	wallEntry := widget.NewEntry()
	wallEntry.SetText("0.8")

	// Binding and log output widget
	logBinding := binding.NewString()
	logBox := widget.NewMultiLineEntry()
	logBinding.AddListener(binding.NewDataListener(func() {
		value, _ := logBinding.Get()
		logBox.SetText(value)
	}))

	var runBtn *widget.Button
	var form fyne.CanvasObject

	// File browser dialog for selecting input STL
	browseBtn := widget.NewButton("📂 Select File", func() {
		fileOpen := dialog.NewFileOpen(func(reader fyne.URIReadCloser, err error) {
			if reader != nil {
				path := reader.URI().Path()
				inEntry.SetText(path)
				dir := filepath.Dir(path)
				base := filepath.Base(path)
				name := strings.TrimSuffix(base, filepath.Ext(base))
				shellEntry.SetText(filepath.Join(dir, name+"_shell.stl"))
				coreEntry.SetText(filepath.Join(dir, name+"_core.stl"))
			}
		}, w)
		fileOpen.Resize(w.Canvas().Size())
		fileOpen.Show()
	})

	// Run button: triggers Blender hollowing
	runBtn = widget.NewButton("🛠 Generate Hollow Model", func() {
		runBtn.Disable()
		logBinding.Set("")

		inFile := inEntry.Text
		shellFile := shellEntry.Text
		coreFile := coreEntry.Text
		wall, _ := strconv.ParseFloat(wallEntry.Text, 64)

		appendLog := func(msg string) {
			current, _ := logBinding.Get()
			logBinding.Set(current + time.Now().Format("15:04:05 ") + msg + "\n")
		}

		go func() {
			blenderExe, err := downloadAndExtractBlender(appendLog)
			if err == nil {
				err = hollowAndCore(blenderExe, inFile, shellFile, coreFile, wall, appendLog)
			}
			if err != nil {
				appendLog("Error: " + err.Error())
			} else {
				appendLog("Done!")
			}
			runBtn.Enable()
		}()
	})

	// Compose the GUI layout
	form = container.NewVBox(
		widget.NewLabel("Input STL File:"),
		container.NewBorder(nil, nil, nil, browseBtn, inEntry),
		widget.NewLabel("Output Shell STL File:"),
		shellEntry,
		widget.NewLabel("Output Core STL File:"),
		coreEntry,
		widget.NewLabel("Wall Thickness (mm):"),
		wallEntry,
		runBtn,
		widget.NewLabel("Log Output:"),
		logBox,
	)

	w.SetContent(container.NewScroll(form))
	w.ShowAndRun()
}

// Entry point: run GUI if no args, else run CLI
func main() {
	if len(os.Args) == 1 {
		runGUI()
		return
	}

	if len(os.Args) != 5 {
		fmt.Fprintf(os.Stderr, "Usage: %s input.stl shell.stl core.stl wall\n",
			filepath.Base(os.Args[0]))
		os.Exit(1)
	}
	inSTL, shellSTL, coreSTL := os.Args[1], os.Args[2], os.Args[3]
	wall, err := strconv.ParseFloat(os.Args[4], 64)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Invalid wall:", err)
		os.Exit(1)
	}

	logger := func(msg string) { fmt.Println(msg) }
	blenderExe, err := downloadAndExtractBlender(logger)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	if err := hollowAndCore(blenderExe, inSTL, shellSTL, coreSTL, wall, logger); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
}
