@echo off
title Media Core DL Server
color 0B

echo =======================================================
echo      Starting Media Core DL (Universal Downloader)
echo =======================================================
echo.
echo [INFO] Keep this black window open while using the app.
echo [INFO] To shut down the app, simply close this window.
echo.

:: สั่งให้รอ 2 วินาทีแล้วเปิด Browser อัตโนมัติ (ทำงานอยู่เบื้องหลัง)
start /b cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: รันเซิร์ฟเวอร์ Python
python "FB DL.py"

echo.
echo Server has stopped.
pause
