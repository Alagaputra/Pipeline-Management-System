@echo off
set "PHP_INI_SCAN_DIR=%~dp0php-conf.d"
if "%~1"=="artisan" if "%~2"=="serve" goto serve
php.exe %*
exit /b %errorlevel%
:serve
php.exe %* --no-reload
exit /b %errorlevel%
