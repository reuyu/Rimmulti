@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0QA-Tactical-Engine\REMOTE-PRESENTATION-20261002\Launch_Manual_QA.ps1"
if errorlevel 1 pause
