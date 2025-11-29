@echo off
REM install_modules.bat
REM Create a venv, install Python dependencies and check for Tesseract

SETLOCAL EnableDelayedExpansion
echo ==================================================
echo GoodDoctorHackingService - Install dependencies
echo ==================================================

REM NOTE: Per user request, this script no longer creates or uses a virtualenv.
REM It installs packages into the system (active) Python environment.
echo Using system Python (do NOT create a venv here).

echo Upgrading pip (system python)...
py -3 -m pip install --upgrade pip

REM Install requirements if present (into system Python)
if exist requirements.txt (
    echo Installing packages from requirements.txt into system Python...
    py -3 -m pip install -r requirements.txt
) else (
    echo requirements.txt not found. Installing core packages into system Python...
    py -3 -m pip install PyQt5 opencv-python numpy Pillow pillow-heif pytesseract
)

REM Quick check for tesseract binary
echo.
echo Checking for Tesseract OCR engine on PATH...
python -c "import shutil,sys; t=shutil.which('tesseract'); print('tesseract on PATH:', t if t else 'NOT FOUND')"
echo.

REM If easyocr is required, copy dependency model files if provided in project
findstr /I "easyocr" requirements.txt >nul 2>&1
if %ERRORLEVEL%==0 (
    echo EasyOCR detected in requirements.txt.
    set "MODEL_SRC=%cd%\easyocr_models"
    set "MODEL_DST=%USERPROFILE%\.EasyOCR\model"
    if exist "%MODEL_SRC%" (
        echo Copying EasyOCR model files from %MODEL_SRC% to %MODEL_DST% ...
        if not exist "%MODEL_DST%" mkdir "%MODEL_DST%"
        xcopy /Y /I "%MODEL_SRC%\*" "%MODEL_DST%\" >nul
        echo Copied model files.
    ) else (
        echo No local easyocr_models folder found in project.
        echo If you need EasyOCR models, place them in %MODEL_SRC% or download them
        echo and copy into %MODEL_DST% (see README for guidance).
    )
)

echo.
echo NOTE: This script installs the Python wrapper 'pytesseract' (if in requirements), but you must
echo install the Tesseract engine itself separately (see README.md for details).
echo.
echo Installation complete.
pause

ENDLOCAL
