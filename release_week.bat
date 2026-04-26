@echo off
title Release Week - Supply Rates No Dispo

echo.
echo =============================================
echo  PriceTravel Analytics Desk
echo  Release Semanal - Supply Rates No Dispo
echo =============================================
echo.

set /p SEMANA="Ingresa el numero de semana (ej: 17): "

if "%SEMANA%"=="" (
    echo ERROR: Debes ingresar un numero de semana.
    pause
    exit /b
)

set REPO=%USERPROFILE%\Documents\GitHub\Price

if not exist "%REPO%" (
    echo ERROR: No se encontro el repo en %REPO%
    pause
    exit /b
)

set EDITORIAL=%REPO%\rates-nodispo\week-%SEMANA%\Editorial
set ANALISIS=%REPO%\rates-nodispo\week-%SEMANA%\Analisis

echo.
echo Creando carpetas para Week-%SEMANA%...
mkdir "%EDITORIAL%" 2>nul
mkdir "%ANALISIS%" 2>nul
echo OK: Carpetas creadas.
echo.

echo Abriendo carpetas. Pega los archivos del Release:
echo    Editorial: RatesNoDispo_Reporte_Editorial.html
echo    Analisis:  Analisis_Rates_NoDispo_7d.xlsx
echo.
explorer "%EDITORIAL%"
timeout /t 1 >nul
explorer "%ANALISIS%"

echo Cuando hayas copiado los 2 archivos, presiona ENTER...
pause >nul

set /a SEMANA_ANT=%SEMANA%-1
set INDEX=%REPO%\index.html

echo Actualizando index.html: week-%SEMANA_ANT% a week-%SEMANA%...
powershell -Command "(Get-Content '%INDEX%') -replace 'week-%SEMANA_ANT%', 'week-%SEMANA%' | Set-Content '%INDEX%'"
echo OK: index.html actualizado.
echo.

echo Abriendo GitHub Desktop...
start "" "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe"

echo.
echo =============================================
echo  En GitHub Desktop:
echo  Summary: Release Week-%SEMANA% - Rates No Dispo
echo  1. Commit to main
echo  2. Push origin
echo =============================================
echo.
pause
