@echo off
setlocal enabledelayedexpansion

:: === Configuration ===
set SCRIPT_DIR=%~dp0
set SRC_DIR=%SCRIPT_DIR%src\python
set OUTPUT_DIR=%SCRIPT_DIR%build\magnetic_imager
set EXEC_NAME=magnetic_logger_gui

:: === Handle clean option ===
if "%1"=="clean" (
    echo [*] Cleaning previous build...
    rmdir /S /Q "%SCRIPT_DIR%build"
    echo [✔] Clean complete.
    exit /b 0
)

:: === Build with pyinstaller from script dir ===
echo [*] Building executable (single-file distribution)...

pyinstaller ^
    --noconsole --clean --strip --onefile ^
    -n %EXEC_NAME% ^
    --distpath "%OUTPUT_DIR%" ^
    --workpath "%SCRIPT_DIR%build\pyinstaller_work" ^
    --specpath "%SCRIPT_DIR%build\pyinstaller_spec" ^
    "%SRC_DIR%\magnetic_logger_gui.py"

:: === Verify build success ===
if not exist "%OUTPUT_DIR%\%EXEC_NAME%.exe" (
    echo [✘] Build failed: %OUTPUT_DIR%\%EXEC_NAME%.exe not found.
    exit /b 1
)

:: === Copy license files ===
mkdir "%OUTPUT_DIR%\licenses"
copy "%SCRIPT_DIR%\licenses\*" "%OUTPUT_DIR%\licenses\" >nul

echo [✔] Executable created: %OUTPUT_DIR%\%EXEC_NAME%.exe
echo [✔] Licenses copied into %OUTPUT_DIR%
echo [✔] Run with: "%OUTPUT_DIR%\%EXEC_NAME%.exe"

endlocal

