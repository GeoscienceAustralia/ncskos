@ECHO OFF
:: Batch file to invoke ncskosdump Python script in MS-Windows
:: Written by Alex Ip 4/10/2016
:: Example invocation: ncskosdump -hs %HOMEDRIVE%\%HOMEPATH%\git\ncskosdump\ncskosdump\test\sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

:: Assume script is in bin directory under module directory
set PYTHONPATH=%~dp0..;%PYTHONPATH%

python -m ncskosdump %*