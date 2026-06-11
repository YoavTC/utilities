@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: yt-audio URL
    exit /b 1
)

set URL=%*


REM Priority list: wav -> mp3 -> ogg -> fallback best
for %%F in (wav mp3 ogg best) do (
    echo Trying format: %%F
    yt-dlp.exe -f bestaudio -x --audio-format %%F --audio-quality 0 "%URL%"
    if !errorlevel! == 0 (
        echo Download succeeded as %%F
        exit /b 0
    )
)

echo All conversions failed.
exit /b 1
