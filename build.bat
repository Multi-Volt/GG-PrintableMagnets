@echo off
setlocal enabledelayedexpansion
set APP=hollowblender
set VERSION=dev
set BUILD=build
set RELEASE=releases

:: Create necessary directories
if not exist %BUILD% (
    mkdir %BUILD%
)
if not exist %RELEASE% (
    mkdir %RELEASE%
)

:: Copy licenses if needed
if not exist %BUILD%\licenses (
    if exist licenses (
        xcopy /E /I /Y licenses %BUILD%\licenses >nul
    )
)

echo Building Windows/amd64

set GOOS=windows
set GOARCH=amd64
go build -trimpath -ldflags "-H=windowsgui -s -w -X main.version=%VERSION%" -o %BUILD%\%APP%_win.exe ./src

:: Strip if possible
where strip >nul 2>nul
if %errorlevel%==0 (
    strip --strip-unneeded %BUILD%\%APP%_win.exe
) else (
    echo (Skipping strip: not found)
)

:: Create zip archive
set ARCHIVE=%RELEASE%\%APP%_win_%VERSION%.zip
powershell -Command "Compress-Archive -Path '%BUILD%\%APP%_win.exe','%BUILD%\licenses' -DestinationPath '%ARCHIVE%'"

echo Done:
dir /b %BUILD%\%APP%_win.exe
dir /b %ARCHIVE%

endlocal

