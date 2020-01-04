for /f "delims=" %%i in ('dir /b %cd%\*.apk') do del /q /s %%i 
