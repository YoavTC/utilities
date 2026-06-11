@echo off
REM shrink_video.bat
REM Usage: shrink_video input.mp4 output.mp4 target_size_in_MB

set "INPUT=%~1"
REM set "OUTPUT=%~2"
set "TARGET_MB=%~2"

REM Default to 9.5 MB if not provided
if "%TARGET_MB%"=="" (
    set "TARGET_MB=9.5"
    echo No target size specified. Defaulting to 9.5 MB
)

set "AUDIO_BITRATE_K=96"

REM Get duration in seconds (truncate decimals)
for /f "tokens=* usebackq" %%a in (`ffprobe -v error -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 "%INPUT%"`) do set "DURATION=%%a"
for /f "tokens=1 delims=." %%b in ("%DURATION%") do set /a "DURATION_INT=%%b"

REM Convert MB to total kilobits
set /a "TOTAL_BITS=%TARGET_MB:.=0% * 819"  REM rough equivalent to *8192 but avoids decimals
set /a "VIDEO_BITRATE_K=(TOTAL_BITS / DURATION_INT) - AUDIO_BITRATE_K"

echo Duration: %DURATION_INT% sec
echo Target size: %TARGET_MB% MB
echo Estimated video bitrate: %VIDEO_BITRATE_K% kbps

REM Get file extension
set "INPUT_NO_EXT=%INPUT%"
for %%f in ("%INPUT%") do (
	set "INPUT_NO_EXT=%%~nf"
	set "EXTENSION=%%~xf"
)

REM Encode
ffmpeg -i "%INPUT%" -c:v libx264 -b:v %VIDEO_BITRATE_K%k -preset faster -c:a aac -b:a %AUDIO_BITRATE_K%k -movflags +faststart -vf "scale='min(640,iw)':'-2'" "%INPUT_NO_EXT%_shrink%EXTENSION%"
