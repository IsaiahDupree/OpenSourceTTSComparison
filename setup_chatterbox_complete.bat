@echo off
echo 🚀 Setting up ChatterBox TTS with GPU support in virtual environment
echo =================================================================

:: Check if virtual environment exists
if not exist "venv_chatterbox" (
    echo Creating virtual environment...
    python -m venv venv_chatterbox
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        exit /b 1
    )
)

echo ✅ Virtual environment ready

:: Activate virtual environment
echo Activating virtual environment...
call venv_chatterbox\Scripts\activate.bat

:: Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

:: Install CUDA-enabled PyTorch
echo 🔥 Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

:: Install audio processing libraries
echo 🎵 Installing audio processing libraries...
pip install soundfile librosa numpy scipy

:: Install ML libraries
echo 🤖 Installing ML libraries...
pip install transformers datasets accelerate

:: Install ChatterBox TTS
echo 💬 Installing ChatterBox TTS...
pip install chatterbox-tts

:: Test CUDA availability
echo 🧪 Testing CUDA availability...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

:: Test ChatterBox import
echo 🧪 Testing ChatterBox import...
python -c "import chatterbox; print('✅ ChatterBox imported successfully')"

echo.
echo 🎉 Setup complete!
echo.
echo 📋 To use ChatterBox:
echo 1. Activate environment: call venv_chatterbox\Scripts\activate.bat
echo 2. Run tests: python test_chatterbox.py
echo 3. Start training your voice model
echo.
pause
