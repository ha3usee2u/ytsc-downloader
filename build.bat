@echo off
set MAIN_SCRIPT=main.py
set ICON_FILE=icon.ico
set PYINSTALLER=pyinstaller

REM 🔍 檢查 yt-dlp.exe 是否存在，否則下載
IF NOT EXIST yt-dlp.exe (
    echo ⬇️ 正在下載 yt-dlp.exe...
    powershell -Command "Invoke-WebRequest https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -OutFile yt-dlp.exe"
)

REM 🔍 檢查 ffmpeg.exe 是否存在，否則下載（使用 gyan.dev 提供的 Windows build）
IF NOT EXIST ffmpeg.exe (
    echo ⬇️ 正在下載 ffmpeg.exe...
    powershell -Command "Invoke-WebRequest https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -OutFile ffmpeg.zip"
    powershell -Command "Expand-Archive ffmpeg.zip -DestinationPath ffmpeg_temp"
    copy /Y ffmpeg_temp\ffmpeg-*\bin\ffmpeg.exe ffmpeg.exe
    rmdir /s /q ffmpeg_temp
    del ffmpeg.zip
)

echo 🔧 清除舊打包資料...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
del /q __pycache__\*.pyc 2>nul

echo 🛠 檢查圖示檔是否存在：%ICON_FILE%
IF EXIST %ICON_FILE% (
    echo ✅ 找到圖示檔，使用圖示打包...
    %PYINSTALLER% --onefile --windowed %MAIN_SCRIPT% ^
     --add-data "yt-dlp.exe;." ^
     --add-data "ffmpeg.exe;." ^
     --icon=%ICON_FILE%
) ELSE (
    echo ⚠️ 沒有圖示檔，略過 --icon 打包...
    %PYINSTALLER% --onefile --windowed %MAIN_SCRIPT% ^
     --add-data "yt-dlp.exe;." ^
     --add-data "ffmpeg.exe;."
)

echo ✅ 打包完成！請查看 dist 資料夾中的 .exe 執行檔
pause
