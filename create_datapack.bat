@echo off
setlocal enabledelayedexpansion

:: Check if namespace was provided as argument
if "%~1"=="" (
    set /p NAMESPACE="Enter the datapack namespace: "
) else (
    set "NAMESPACE=%~1"
)

:: Validate namespace is not empty
if "!NAMESPACE!"=="" (
    echo Error:  Namespace cannot be empty! 
    exit /b 1
)

echo Creating datapack structure with namespace:  !NAMESPACE!
echo. 

::  Create folder structure
echo Creating folders...  

:: Create base data directory
if not exist "data" mkdir "data"

:: Create minecraft directory structure
if not exist "data\minecraft" mkdir "data\minecraft"
if not exist "data\minecraft\tags" mkdir "data\minecraft\tags"
if not exist "data\minecraft\tags\function" mkdir "data\minecraft\tags\function"

:: Create namespace directory - store in variable for clarity
set "NS_PATH=data\!NAMESPACE!"
echo Creating namespace folder: !NS_PATH! 
if not exist "!NS_PATH!" mkdir "!NS_PATH!"

:: Create namespace subdirectories
if not exist "!NS_PATH!\advancement" mkdir "!NS_PATH!\advancement"
if not exist "!NS_PATH!\advancement\_events" mkdir "!NS_PATH!\advancement\_events"
if not exist "!NS_PATH!\function" mkdir "!NS_PATH!\function"
if not exist "!NS_PATH!\function\_events" mkdir "!NS_PATH!\function\_events"
if not exist "! NS_PATH!\loot_table" mkdir "!NS_PATH!\loot_table"
if not exist "!NS_PATH!\recipe" mkdir "!NS_PATH!\recipe"
if not exist "! NS_PATH!\predicate" mkdir "!NS_PATH!\predicate"
if not exist "!NS_PATH!\tags" mkdir "!NS_PATH!\tags"
if not exist "!NS_PATH!\tags\block" mkdir "!NS_PATH!\tags\block"
if not exist "! NS_PATH!\tags\item" mkdir "!NS_PATH!\tags\item"
if not exist "!NS_PATH!\tags\entity_type" mkdir "!NS_PATH!\tags\entity_type"

:: Create pack.mcmeta
echo Creating pack.mcmeta...
(
echo {
echo 	"pack": {
echo 		"description": [
echo 			{
echo 				"text": "!NAMESPACE! v1.0\n",
echo 				"color": "dark_gray"
echo 			},
echo 			{
echo 				"text": "www.yoavtc.work",
echo 				"color": "blue",
echo 				"underlined": true
echo 			}
echo 		],
echo 		"min_format": X,
echo 		"max_format": Y
echo 	}
echo }
) > "pack.mcmeta"

:: Create load.json
echo Creating load.json...
(
echo {
echo     "values": [
echo         "!NAMESPACE!:_load"
echo     ]
echo }
) > "data\minecraft\tags\function\load.json"

:: Create tick.json
echo Creating tick. json...
(
echo {
echo     "values": [
echo         "!NAMESPACE!:_tick"
echo     ]
echo }
) > "data\minecraft\tags\function\tick.json"

:: Create _load.mcfunction
echo Creating _load.mcfunction...
(
echo( 
) > "!NS_PATH!\function\_load.mcfunction"

:: Create _tick. mcfunction
echo Creating _tick. mcfunction...
(
echo(
) > "!NS_PATH!\function\_tick.mcfunction"

echo.
echo ============================================
echo Datapack structure created successfully! 
echo Namespace: !NAMESPACE!
echo Location: %CD%
echo ============================================
echo.  