@echo off
echo Setting up Chatterbox TTS environment...

REM Create virtual environment
echo Creating virtual environment...
python -m venv envs\venv_chatterbox
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    exit /b 1
)

REM Activate environment and install packages
echo Activating environment and installing packages...
call envs\venv_chatterbox\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install compatible torch versions
echo Installing PyTorch 1.13.1...
pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cpu

REM Install transformers compatible version
echo Installing compatible transformers...
pip install transformers==4.21.3

REM Install other dependencies
echo Installing other dependencies...
pip install numpy soundfile

REM Install chatterbox-tts
echo Installing chatterbox-tts...
pip install chatterbox-tts

echo Chatterbox environment setup complete!
echo To activate: envs\venv_chatterbox\Scripts\activate.bat
