@echo off
setlocal

set "self=%~nx0"
echo Files in %~dp0:
echo ------------------

for %%F in ("%~dp0*") do (
    if /i not "%%~nxF"=="%self%" if not "%%~aF"=="d" echo %%~nxF
)

endlocal
