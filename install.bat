@echo off
REM Create conda env, install Python 3.10+, pip install requirements (benchmark reproducibility).
set ENV_NAME=2d-bin-packing
where conda >nul 2>nul
if errorlevel 1 (
  echo Conda not found in PATH. Install Miniconda/Anaconda or use: pip install -r requirements.txt
  exit /b 1
)
call conda create -n %ENV_NAME% python=3.11 -y
if errorlevel 1 exit /b 1
call conda activate %ENV_NAME%
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
echo.
echo Done. Activate with: conda activate %ENV_NAME%
echo Run app: python -m App.main
echo Verify: python verify.py
