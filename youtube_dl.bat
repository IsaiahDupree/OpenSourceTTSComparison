@echo off
:: YouTube Downloader Batch File (2025)
:: Uses direct yt-dlp commands for maximum reliability
:: 
:: Usage:
::   youtube_dl.bat [options] URL
::
:: Options:
::   -v        Download video (MP4)
::   -a        Download audio only (M4A)
::   -p        Create playlist folder structure
::   -u        Update yt-dlp
::
:: Examples:
::   youtube_dl.bat -a https://www.youtube.com/watch?v=L6yKk7EQYZc
::   youtube_dl.bat -v -p https://www.youtube.com/playlist?list=XXXX

setlocal enabledelayedexpansion

echo 🎬 YouTube Downloader (yt-dlp)
echo =============================================

:: Default values
set "OUTPUT_DIR=custom_output"
set "DOWNLOAD_TYPE=audio"
set "PLAYLIST_STRUCTURE=false"
set "UPDATE_YTDLP=false"
set "URL="

:: Parse arguments
:parse_args
if "%~1"=="" goto :check_args
if "%~1"=="-v" (
    set "DOWNLOAD_TYPE=video"
    shift
    goto :parse_args
)
if "%~1"=="-a" (
    set "DOWNLOAD_TYPE=audio"
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set "PLAYLIST_STRUCTURE=true"
    shift
    goto :parse_args
)
if "%~1"=="-u" (
    set "UPDATE_YTDLP=true"
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set "OUTPUT_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    goto :show_help
)
if "%~1"=="--help" (
    goto :show_help
)
set "URL=%~1"
shift
goto :parse_args

:check_args
if "%URL%"=="" (
    echo ❌ Error: No URL provided
    goto :show_help
)

:: Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: Update yt-dlp if requested
if "%UPDATE_YTDLP%"=="true" (
    echo Updating yt-dlp...
    yt-dlp -U
    if !errorlevel! neq 0 (
        echo ❌ Failed to update yt-dlp
        echo Please install yt-dlp manually from: https://github.com/yt-dlp/yt-dlp#installation
        exit /b 1
    )
)

:: Check if yt-dlp is installed
yt-dlp --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ yt-dlp is not installed or not in PATH
    echo Please install yt-dlp from: https://github.com/yt-dlp/yt-dlp#installation
    exit /b 1
)

:: Build the command
set "CMD=yt-dlp"

:: Add format options based on download type
if "%DOWNLOAD_TYPE%"=="video" (
    :: Best MP4 (prefers video+audio merged, needs ffmpeg)
    set "CMD=!CMD! -S res,ext:mp4:m4a -f bv*+ba/b"
) else (
    :: Audio-only M4A
    set "CMD=!CMD! -f bestaudio[ext=m4a]/bestaudio"
)

:: Add output template
if "%PLAYLIST_STRUCTURE%"=="true" (
    set "CMD=!CMD! -o "%OUTPUT_DIR%/%%%(uploader)s/%%%(playlist)s/%%%(playlist_index)s - %%%(title).200B.%%%(ext)s""
) else (
    set "CMD=!CMD! -o "%OUTPUT_DIR%/%%%(id)s_%%%(title).200B.%%%(ext)s""
)

:: Add URL
set "CMD=!CMD! %URL%"

echo Running: !CMD!
echo.

:: Execute command
%CMD%

if %errorlevel% equ 0 (
    echo.
    echo ✅ Download successful!
    echo 📂 Output directory: %OUTPUT_DIR%
    exit /b 0
) else (
    echo.
    echo ❌ Download failed with error code: %errorlevel%
    exit /b %errorlevel%
)

:show_help
echo.
echo Usage: youtube_dl.bat [options] URL
echo.
echo Options:
echo   -v        Download video (MP4)
echo   -a        Download audio only (M4A) [default]
echo   -p        Create playlist folder structure
echo   -o DIR    Output directory (default: custom_output)
echo   -u        Update yt-dlp
echo   -h        Show this help message
echo.
echo Examples:
echo   youtube_dl.bat -a https://www.youtube.com/watch?v=L6yKk7EQYZc
echo   youtube_dl.bat -v -p https://www.youtube.com/playlist?list=XXXX
echo.
exit /b 1
