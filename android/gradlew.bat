@echo off
REM StockLens AI lightweight Gradle launcher for Windows.
REM If this fails, install Android Studio or Gradle 8.14.4 and run gradle directly.
where gradle >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  gradle %*
  exit /b %ERRORLEVEL%
)
echo Gradle is not installed. Install Android Studio or Gradle 8.14.4, then rerun this command.
exit /b 1
