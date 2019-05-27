@ECHO off
SET Nuke_ROOT=C:\Program Files\Nuke11.0v1
SET PATH=%PATH%;%Nuke_ROOT%

SET TOOLS_PATH=V:\PipelineTool\NukeTools
SET NUKE_PATH=%NUKE_PATH%;%TOOLS_PATH%

ECHO [OF] Info: Launch %Nuke_ROOT%\Nuke11.0exe %*
Nuke11.0.exe %*
pause
