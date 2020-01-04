for /f "delims=" %%i in ('dir /b %cd%\*.apk') do set file=%%i 
java -jar %~dp0signapk.jar %~dp0platform.x509.pem %~dp0platform.pk8  %file%  %~dp0sign.apk &&(
adb install -r %~dp0sign.apk)
pause