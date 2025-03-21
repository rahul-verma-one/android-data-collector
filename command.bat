@echo off
setlocal

set "package_name=com.facebook.katana"

for /f "tokens=*" %%i in ('adb shell pidof "%package_name%"') do set "pid=%%i"

if "%pid%"=="" (
  echo Package "%package_name%" not found.
  goto end
)
echo PID of "%package_name%": %pid%

set "count=0"
:loop
if %count% equ 10 goto end

echo Running top command (iteration %count% + 1)...
adb shell "top -n 1 -b -p %pid%"
if errorlevel 1 (
  echo Error running adb shell top. Check adb connection.
  goto end
)

set /a count+=1
goto loop

:end
echo Finished running top command 10 times.
endlocal