@echo off
cd /d "%~dp0"
set "PATH=%~dp0Graphviz\bin;%PATH%"
python src\main.py %*